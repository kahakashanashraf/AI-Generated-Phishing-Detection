"""Unit tests for the Study 2 shared library (phishbench). Run: python -m unittest discover -s tests -v"""

import json
import mailbox
import sys
import tempfile
import unittest
from email.message import EmailMessage
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from phishbench import stats, textnorm  # noqa: E402
from phishbench.dedup import LSHIndex, MinHasher, UnionFind, estimated_jaccard, shingles  # noqa: E402
from phishbench.freeze import Decontaminator, proportional_allocation, seeded_order, select_cell  # noqa: E402
from phishbench.loaders import clean_foia, load_nazario_mbox, message_body, record  # noqa: E402
from phishbench.manifest import sha256_of_ids, write_json  # noqa: E402

LOREM = ("please find attached the quarterly budget report for the northeast region and let me know "
         "if you have any questions about the forecast numbers before the meeting on thursday afternoon "
         "we also need to confirm the venue for the offsite and the list of attendees from each team")


class TestTextnorm(unittest.TestCase):
    def test_normalize_and_key(self):
        self.assertEqual(textnorm.normalize("  Hello \n WORLD "), "hello world")
        self.assertEqual(textnorm.text_key("Hi", "A  b"), textnorm.text_key("hi", "a b"))
        self.assertNotEqual(textnorm.text_key("Hi", "a b"), textnorm.text_key("Hi", "a c"))

    def test_placeholder_roundtrip(self):
        text = "Visit https://example.org/a?b=1 or mail bob@corp.com, call +1 (555) 123-4567. Again https://example.org/a?b=1"
        locked, mapping = textnorm.lock_placeholders(text)
        self.assertNotIn("example.org", locked)
        self.assertIn("[URL_1]", locked)
        self.assertEqual(locked.count("[URL_1]"), 2)  # identical strings share one token
        self.assertIn("[EMAIL_1]", locked)
        self.assertIn("[PHONE_1]", locked)
        self.assertEqual(textnorm.restore_placeholders(locked, mapping), text)

    def test_placeholders_preserved(self):
        src = "Click [URL_1] or reply to [EMAIL_1]"
        self.assertTrue(textnorm.placeholders_preserved(src, "Reply [EMAIL_1]; link: [URL_1]."))
        self.assertFalse(textnorm.placeholders_preserved(src, "Click [URL_1]"))
        self.assertFalse(textnorm.placeholders_preserved(src, "[URL_1] [EMAIL_1] [URL_2]"))

    def test_split_subject_and_html(self):
        self.assertEqual(textnorm.split_subject("Subject: Lunch\nSee you at noon"), ("Lunch", "See you at noon"))
        self.assertEqual(textnorm.split_subject("No subject here"), ("", "No subject here"))
        txt = textnorm.html_to_text("<html><head><style>x{}</style></head><body><p>Hello</p><script>bad()</script>World</body></html>")
        self.assertIn("Hello", txt)
        self.assertIn("World", txt)
        self.assertNotIn("bad()", txt)

    def test_refusal(self):
        self.assertTrue(textnorm.is_refusal("I'm sorry, but I can't help with that."))
        self.assertFalse(textnorm.is_refusal("Subject: Meeting\nHi team, see you soon."))


class TestDedup(unittest.TestCase):
    def setUp(self):
        self.h = MinHasher(num_perm=128, seed=2026)

    def test_deterministic(self):
        s = shingles(LOREM)
        np.testing.assert_array_equal(self.h.signature(s), MinHasher(128, 2026).signature(s))

    def test_near_duplicate_linked_distinct_not(self):
        a = self.h.signature(shingles(LOREM))
        b = self.h.signature(shingles(LOREM.replace("thursday", "friday")))
        c = self.h.signature(shingles("completely different text about football scores and weather in spring " * 3))
        self.assertGreater(estimated_jaccard(a, b), 0.6)
        self.assertLess(estimated_jaccard(a, c), 0.1)
        idx = LSHIndex(128, 16, 0.5)
        idx.add("a", a)
        self.assertEqual(idx.query(b), ["a"])
        self.assertEqual(idx.query(c), [])

    def test_union_find(self):
        uf = UnionFind()
        uf.union(1, 2)
        uf.union(3, 4)
        uf.union(2, 4)
        uf.find(5)
        groups = sorted(sorted(g) for g in uf.groups().values())
        self.assertEqual(groups, [[1, 2, 3, 4], [5]])


class TestStats(unittest.TestCase):
    def test_threshold_matches_n05_rule(self):
        y = [0] * 30 + [1] * 20
        s = np.linspace(0, 1, 50)
        t = stats.threshold_at_fpr(y, s, 0.05)
        neg = s[:30]
        self.assertLessEqual(np.mean(neg >= t), 0.05)
        self.assertGreater(t, 0)
        with self.assertRaises(ValueError):
            stats.threshold_at_fpr([0] * 5 + [1] * 5, np.arange(10))

    def test_wilson(self):
        lo, hi = stats.wilson_ci(16, 142)
        self.assertAlmostEqual(lo, 0.0708, places=3)
        self.assertAlmostEqual(hi, 0.1749, places=3)
        self.assertEqual(stats.wilson_ci(0, 10)[0], 0.0)

    def test_mcnemar(self):
        self.assertEqual(stats.mcnemar_exact(0, 0), 1.0)
        self.assertEqual(stats.mcnemar_exact(1, 0), 1.0)
        self.assertAlmostEqual(stats.mcnemar_exact(0, 5), 0.0625)
        self.assertAlmostEqual(stats.mcnemar_exact(5, 0), 0.0625)

    def test_cluster_bootstrap_and_tost(self):
        rng = np.random.default_rng(0)
        clusters = np.repeat(np.arange(500), 2)
        ref = rng.integers(0, 2, size=1000)
        boot = stats.cluster_bootstrap_delta(clusters, ref, ref.copy(), iterations=2000, seed=1)
        self.assertEqual(boot["delta"], 0.0)
        self.assertTrue(stats.tost_equivalent(boot, 0.03))
        shifted = ref.copy()
        shifted[ref == 0] = 1
        boot2 = stats.cluster_bootstrap_delta(clusters, ref, shifted, iterations=2000, seed=1)
        self.assertGreater(boot2["ci95"][0], 0.3)
        self.assertFalse(stats.tost_equivalent(boot2, 0.03))
        again = stats.cluster_bootstrap_delta(clusters, ref, shifted, iterations=2000, seed=1)
        self.assertEqual(boot2, again)

    def test_holm(self):
        adj = stats.holm({"a": 0.01, "b": 0.04, "c": 0.03})
        self.assertAlmostEqual(adj["a"], 0.03)
        self.assertAlmostEqual(adj["c"], 0.06)
        self.assertAlmostEqual(adj["b"], 0.06)


class TestManifest(unittest.TestCase):
    def test_write_json_real_newline(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.json"
            write_json(p, {"a": 1})
            raw = p.read_bytes()
            self.assertTrue(raw.endswith(b"}\n"))
            self.assertNotIn(b"\\n", raw)
            self.assertEqual(json.loads(raw), {"a": 1})

    def test_id_fingerprint_order_free(self):
        self.assertEqual(sha256_of_ids(["b", "a"]), sha256_of_ids(["a", "b"]))


class TestFreeze(unittest.TestCase):
    def setUp(self):
        self.h = MinHasher(128, 2026)

    def _rec(self, i, body, subject="s"):
        return record(f"x:{i}", "x", i, subject, body, 0, "human")

    def test_select_cell_decontaminates_and_dedups(self):
        protected = Decontaminator(self.h)
        protected.add(self._rec("p", LOREM))
        cands = [
            self._rec(1, LOREM),                                   # exact duplicate of protected
            self._rec(2, LOREM.replace("thursday", "friday")),     # near-duplicate of protected
            self._rec(3, "a new message about the server migration schedule next week and backups " * 2),
            self._rec(4, "a new message about the server migration schedule next week and backups " * 2),
            self._rec(5, ""),
        ]
        kept, why = select_cell(cands, None, 2026, protected, self.h, require_english=False)
        self.assertEqual(len(kept), 1)
        self.assertEqual(why["linked_to_train_or_val"], 2)
        self.assertEqual(why["near_duplicate_within_cell"], 1)
        self.assertEqual(why["empty_body"], 1)

    def test_seeded_order_input_order_free(self):
        recs = [self._rec(i, str(i)) for i in range(20)]
        a = [r["sample_id"] for r in seeded_order(recs, 7)]
        b = [r["sample_id"] for r in seeded_order(list(reversed(recs)), 7)]
        self.assertEqual(a, b)

    def test_proportional_allocation(self):
        self.assertEqual(proportional_allocation({"a": 10, "b": 5}, 100), {"a": 10, "b": 5})
        alloc = proportional_allocation({2023: 600, 2024: 1200, 2025: 1500}, 2000)
        self.assertEqual(sum(alloc.values()), 2000)
        self.assertTrue(all(alloc[k] <= v for k, v in {2023: 600, 2024: 1200, 2025: 1500}.items()))


class TestLoaders(unittest.TestCase):
    def test_mbox_parsing_and_notice_removal(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "phishing-2023"
            box = mailbox.mbox(str(path))
            m1 = EmailMessage()
            m1["Subject"] = "Your account is locked"
            m1.set_content("Dear user, verify now.")
            m1.add_alternative("<p>Dear user, <b>verify</b> now.</p>", subtype="html")
            m2 = EmailMessage()
            m2["Subject"] = "DON'T DELETE THIS MESSAGE -- FOLDER INTERNAL DATA"
            m2.set_content("internal")
            m3 = EmailMessage()
            m3["Subject"] = "=?utf-8?b?SW52b2ljZSBkdWU=?="
            m3.add_alternative("<html><body><p>Pay invoice</p></body></html>", subtype="html")
            for m in (m1, m2, m3):
                box.add(m)
            box.flush()
            box.close()
            recs, removed = load_nazario_mbox(path, 2023)
            self.assertEqual(removed, 1)
            self.assertEqual(len(recs), 2)
            self.assertEqual(recs[0]["body"], "Dear user, verify now.")
            self.assertEqual(recs[1]["subject"], "Invoice due")
            self.assertIn("Pay invoice", recs[1]["body"])
            self.assertEqual(recs[0]["authorship"], "unknown")
            self.assertTrue(all(r["label"] == 1 for r in recs))

    def test_message_body_skips_attachments(self):
        m = EmailMessage()
        m.set_content("visible text")
        m.add_attachment(b"binary", maintype="application", subtype="octet-stream", filename="x.bin")
        self.assertEqual(message_body(m), "visible text")

    def test_clean_foia(self):
        body = "UNCLASSIFIED U.S. Department of State Case No. F-2014-20439 Doc No. C05739545\nLet's meet at 3.\n"
        self.assertEqual(clean_foia(body), "Let's meet at 3.")


if __name__ == "__main__":
    unittest.main()


class TestGeneration(unittest.TestCase):
    def setUp(self):
        from phishbench import generation
        self.g = generation
        self.parent = record("x:1", "x", 1, "Invoice for March",
                             "Hi Ann, the invoice is at https://corp.example.com/inv/3 and questions go to bob@corp.com. "
                             "Please pay by Friday. Thanks, Bob", 0, "human")

    def test_prompts_frozen_phrases(self):
        self.assertIn("Correct only the spelling, grammar and punctuation", self.g.PROMPTS["L1"])
        self.assertIn("Polish the following email so that it is clear, fluent and professional", self.g.PROMPTS["L2"])
        self.assertIn("Do not add or remove links, attachments, requests, or deadlines", self.g.PROMPTS["L3"])
        self.assertIn("Write a realistic, legitimate email with the subject line below", self.g.PROMPTS["L4"])
        self.assertEqual(self.g.DECODING["temperature"], 0.7)

    def test_request_locks_security_evidence(self):
        req = self.g.build_request(self.parent, "L3")
        self.assertNotIn("corp.example.com", req["prompt"])
        self.assertIn("[URL_1]", req["prompt"])
        self.assertIn("[EMAIL_1]", req["prompt"])

    def test_quality_check_accepts_and_restores(self):
        req = self.g.build_request(self.parent, "L3")
        out = ("Subject: March invoice\nHello Ann, you can find the invoice at [URL_1]; send any questions to "
               "[EMAIL_1]. Kindly settle it by Friday. Best, Bob")
        res, why = self.g.quality_check(self.parent, "L3", req, out, check_language=False)
        self.assertIsNone(why)
        self.assertIn("https://corp.example.com/inv/3", res["body"])
        self.assertIn("bob@corp.com", res["body"])

    def test_quality_check_rejections(self):
        req = self.g.build_request(self.parent, "L3")
        self.assertEqual(self.g.quality_check(self.parent, "L3", req, "I'm sorry, I can't help.", False)[1], "refusal")
        self.assertEqual(self.g.quality_check(self.parent, "L3", req, "no subject line here", False)[1], "unparseable")
        dropped = "Subject: x\nHello Ann, the invoice is ready, pay by Friday, mail [EMAIL_1] with questions please. Bob"
        self.assertEqual(self.g.quality_check(self.parent, "L3", req, dropped, False)[1], "placeholders_changed")

    def test_l1_identical_output_allowed(self):
        req = self.g.build_request(self.parent, "L1")
        same = "Subject: Invoice for March\n" + textnorm.lock_placeholders(
            self.parent["subject"] + "\n⁣\n" + self.parent["body"])[0].split("\n⁣\n", 1)[1]
        res, why = self.g.quality_check(self.parent, "L1", req, same, check_language=False)
        self.assertIsNone(why)
        self.assertEqual(self.g.quality_check(self.parent, "L3", self.g.build_request(self.parent, "L3"), same, False)[1],
                         "identical_to_input")

    def test_dn_url_placeholder_and_seed(self):
        req = self.g.build_request(self.parent, "L4")
        out = "Subject: Invoice for March\n" + " ".join(["word"] * 60) + " see [URL_1]"
        res, why = self.g.quality_check(self.parent, "L4", req, out, check_language=False)
        self.assertIsNone(why)
        self.assertIn(self.g.DN_URL, res["body"])
        self.assertEqual(self.g.batch_seed(["b", "a"]), self.g.batch_seed(["a", "b"]))


class TestGrecoParser(unittest.TestCase):
    def test_quoted_and_unquoted_files(self):
        from phishbench.loaders import greco_rows, load_greco_llm
        with tempfile.TemporaryDirectory() as d:
            base = Path(d) / "llm-generated"
            base.mkdir()
            (base / "legit.csv").write_bytes(b'text,label\r\n"Dear team, the meeting moved to 3pm, see ""agenda"".",1\r\n')
            (base / "phishing.csv").write_bytes(b"text,label\r\nDear User, verify your account, now, or lose access,1\r\n")
            self.assertEqual(greco_rows(base / "phishing.csv"), ["Dear User, verify your account, now, or lose access"])
            self.assertEqual(greco_rows(base / "legit.csv"), ['Dear team, the meeting moved to 3pm, see "agenda".'])
            recs = load_greco_llm(Path(d))
            self.assertEqual([r["label"] for r in recs], [0, 1])  # label from the file name, not the authorship column


class TestModels(unittest.TestCase):
    def setUp(self):
        from phishbench import models
        self.m = models
        rng = np.random.default_rng(0)
        legit = ["meeting agenda for the quarterly budget review with the finance team",
                 "lunch plans and the project timeline for next week, see attached notes",
                 "please review the draft report and send comments before friday"]
        phish = ["verify your account password now or it will be suspended click the link",
                 "urgent your bank account is locked confirm your login details immediately",
                 "you won a prize claim your reward by entering your card number today"]
        self.texts = [legit[i % 3] + f" ref {i}" for i in range(60)] + [phish[i % 3] + f" id {i}" for i in range(60)]
        self.y = np.array([0] * 60 + [1] * 60)
        self.groups = np.arange(120) // 2

    def test_balanced_weights_match_sklearn(self):
        from sklearn.utils.class_weight import compute_sample_weight
        y = np.array([0, 0, 0, 1])
        np.testing.assert_allclose(self.m.balanced_weights(y), compute_sample_weight("balanced", y))
        np.testing.assert_allclose(self.m.balanced_weights(y, [2, 1, 1, 1]),
                                   compute_sample_weight("balanced", y) * np.array([2, 1, 1, 1]))

    def test_classical_detectors_learn(self):
        vec = self.m.make_vectorizer().fit(self.texts)
        X = vec.transform(self.texts)
        for clf in (self.m.fit_d1_lr(X, self.y, None, 1.0, 0), self.m.fit_d2_svm(X, self.y, None, 0),
                    self.m.fit_d3_cnb(X, self.y, None, 0.5)):
            self.assertGreater((clf.predict_proba(X)[:, 1] > 0.5).astype(int).tolist().count(1), 50)
        best, scores = self.m.grouped_cv_select(lambda X_, y_, w_, C: self.m.fit_d1_lr(X_, y_, w_, C, 0), [0.1, 1.0, 10.0],
                                                X, self.y, None, self.groups, 0)
        self.assertIn(best, [0.1, 1.0, 10.0])
        self.assertEqual(len(scores), 3)

    def test_consistency_penalty_shrinks_pair_gap(self):
        vec = self.m.make_vectorizer().fit(self.texts)
        X = vec.transform(self.texts)
        P, R = X[:30], X[30:60]   # pairs of legitimate rows with different wording
        free = self.m.ConsistencyLinear(lam=0.0).fit(X, self.y, None, P, R)
        tied = self.m.ConsistencyLinear(lam=50.0).fit(X, self.y, None, P, R)
        gap = lambda mdl: float(np.mean((mdl.decision_function(P) - mdl.decision_function(R)) ** 2))
        self.assertLess(gap(tied), gap(free))
        tied.calibrate(X, self.y)
        p = tied.predict_proba(X)[:, 1]
        self.assertTrue(np.all((p >= 0) & (p <= 1)))
        self.assertGreater(np.mean((p > 0.5) == (self.y == 1)), 0.9)


class TestTransformerHelpers(unittest.TestCase):
    def test_head_tail(self):
        from phishbench.transformer_train import head_tail
        self.assertEqual(head_tail(list(range(5)), 10, 5), [0, 1, 2, 3, 4])
        self.assertEqual(head_tail(list(range(10)), 6, 3), [0, 1, 2, 7, 8, 9])
        self.assertEqual(len(head_tail(list(range(1000)), 254, 127)), 254)


class TestNormalizeAndInterventions(unittest.TestCase):
    def test_artifact_normalize(self):
        t = ("Subject: Invoice 4471\n\nPay $1,200 by 12/05/2024 at https://pay.example.com or mail ap@corp.com.\n"
             "To unsubscribe click here\n-----Original Message-----\nFrom: someone\nold text")
        n = textnorm.artifact_normalize(t)
        for token in ("<URL>", "<EMAIL>", "<DATE>", "<NUM>"):
            self.assertIn(token, n)
        self.assertNotIn("old text", n)
        self.assertNotIn("unsubscribe", n.lower())
        self.assertIn("Subject:", n)

    def test_interventions(self):
        from phishbench import interventions as iv
        body = "Hi Sam,\nThe report is at https://intranet.example.org/r1 for review.\nThanks,\nAlex"
        self.assertIn(iv.I1_LINE, iv.apply("I1", body))
        self.assertNotIn("https://", iv.apply("I2", body))
        self.assertTrue(iv.apply("I3", body).endswith("Northfield Partners Ltd."))
        i4 = iv.apply("I4", body)
        self.assertFalse(i4.lower().startswith("hi"))
        self.assertNotIn("Thanks", i4)
        self.assertIn("unsubscribe", iv.apply("I5", body))
        self.assertLess(len(iv.apply("I6", body).split()), len(body.split()))
        with self.assertRaises(ValueError):
            iv.apply("I9", body)


class TestStatsExtensions(unittest.TestCase):
    def test_tost_p_and_draws(self):
        clusters = np.repeat(np.arange(400), 2)
        ref = np.random.default_rng(1).integers(0, 2, 800)
        b = stats.cluster_bootstrap_delta(clusters, ref, ref, iterations=1000, seed=3, return_draws=True)
        self.assertEqual(len(b["draws"]), 1000)
        self.assertLess(stats.bootstrap_tost_p(b["draws"], 0.03), 0.05)
        far = b["draws"] + 0.10
        self.assertGreater(stats.bootstrap_tost_p(far, 0.03), 0.5)

    def test_alert_budget(self):
        s = np.arange(100) / 100.0
        t = stats.alert_budget_threshold(s, 0.10)
        self.assertAlmostEqual(np.mean(s >= t), 0.10, places=2)

    def test_gee_trend(self):
        try:
            import statsmodels  # noqa: F401
        except ImportError:
            self.skipTest("statsmodels not installed")
        rng = np.random.default_rng(0)
        parents = np.repeat(np.arange(300), 5)
        level = np.tile(np.arange(5), 300)
        p = 1 / (1 + np.exp(-(-2 + 0.6 * level)))
        y = (rng.random(len(p)) < p).astype(int)
        r = stats.gee_trend(y, level, np.where(parents % 2, "a", "b"), parents)
        self.assertEqual(r["status"], "ok")
        self.assertGreater(r["coef"], 0.3)
        self.assertLess(r["p"], 1e-6)
        self.assertEqual(stats.gee_trend(np.zeros(10), np.arange(10), ["a"] * 10, np.arange(10))["status"],
                         "not_estimable_constant_outcome")


def _hv_records():
    gens, recs, parents = ("g1", "g2"), [], {}
    for src in ("EXT", "IN"):
        for lab, kind in ((0, "legit"), (1, "phish")):
            pcell = f"{src}-{kind}-L0" if lab == 0 else f"{src}-{kind}-H"
            for i in range(12):
                pid = f"{pcell}:{i}"
                parents[pid] = {"sample_id": pid, "subject": f"s{i}", "body": f"see http://x.org/{i} and www.y.org"}
                for g in gens:
                    for lv in (("L3", "L4") if lab == 0 else ("L3",)):
                        recs.append({"sample_id": f"{pid}|{lv}|{g}", "native_id": pid, "generator": g, "label": lab,
                                     "level": lv, "cell": f"{src}-{kind}-{lv}-{g}", "subject": "S", "body": f"http://x.org/{i}"})
    return list(gens), recs, parents


class TestHumanValidation(unittest.TestCase):
    def test_sample_items_and_blinding(self):
        from phishbench import human_validation as hv
        gens, recs, parents = _hv_records()
        rw, dn, rep = hv.draw_sample(recs, gens, rw_per_stratum=5, dn_per_stratum=3, seed=1)
        self.assertEqual(len(rw), 2 * 2 * 2 * 5)
        self.assertEqual(len(dn), 2 * 2 * 3)
        self.assertTrue(all(r["parent_reuse"] == 0 for r in rep))
        for src in ("EXT", "IN"):            # disjoint parents across generators within a stratum pair
            for lab in (0, 1):
                ps = [{r["native_id"] for r in rw if r["generator"] == g and hv.source_of(r) == src and r["label"] == lab} for g in gens]
                self.assertFalse(ps[0] & ps[1])
        rw2, dn2, _ = hv.draw_sample(list(reversed(recs)), gens, rw_per_stratum=5, dn_per_stratum=3, seed=1)
        self.assertEqual([r["sample_id"] for r in rw], [r["sample_id"] for r in rw2])     # input-order independent
        items, key = hv.make_items(rw, dn, parents, seed=1)
        self.assertEqual(len(items), len(key))
        self.assertTrue(all("http://" not in x["body"] and "hxxp://" in x["body"] for x in items))
        self.assertTrue(all("www[.]" in x["original_body"] for x in items if x["task"] == "RW"))
        self.assertTrue(all("generator" not in x and "label" not in x for x in items))
        oa, ob = hv.rater_order(items, "A", 1), hv.rater_order(items, "B", 1)
        self.assertEqual(sorted(x["item_id"] for x in oa), sorted(x["item_id"] for x in ob))
        self.assertNotEqual([x["item_id"] for x in oa], [x["item_id"] for x in ob])
        self.assertEqual(hv.items_digest(oa), hv.items_digest(ob))
        # sampling shortfall is filled from the other generator's parents and reported
        _, _, rep3 = hv.draw_sample(recs, gens, rw_per_stratum=8, dn_per_stratum=3, seed=1)
        self.assertTrue(any(r["parent_reuse"] > 0 for r in rep3))
        self.assertTrue(all(r["drawn"] == r["target"] for r in rep3))

    def test_kappa(self):
        from phishbench import human_validation as hv
        self.assertAlmostEqual(hv.cohen_kappa(list("aabb"), list("aabb")), 1.0)
        # kappa equals (po - pe) / (1 - pe) computed by hand
        a = ["y"] * 50 + ["n"] * 50
        b = ["y"] * 20 + ["n"] * 5 + ["y"] * 10 + ["n"] * 15 + ["y"] * 15 + ["n"] * 10 + ["y"] * 5 + ["n"] * 20
        po = sum(x == y for x, y in zip(a, b)) / 100
        ca = {"y": 50, "n": 50}; cb = {"y": b.count("y"), "n": b.count("n")}
        pe = (ca["y"] * cb["y"] + ca["n"] * cb["n"]) / 10000
        self.assertAlmostEqual(hv.cohen_kappa(a, b), (po - pe) / (1 - pe))
        self.assertTrue(np.isnan(hv.cohen_kappa(["x"] * 5, ["x"] * 5)))
        # AC1 stays high under extreme prevalence where kappa collapses to 0
        p, q = ["x"] * 19 + ["x"], ["x"] * 19 + ["y"]
        self.assertAlmostEqual(hv.cohen_kappa(p, q, ["x", "y"]), 0.0)
        pi_y = 1 / 40; pe = 2 * pi_y * (1 - pi_y)
        self.assertAlmostEqual(hv.gwet_ac1(p, q, ["x", "y"]), (0.95 - pe) / (1 - pe))
        lo, hi = hv.kappa_bootstrap_ci(a, b, iterations=300, seed=0)
        self.assertLess(lo, hv.cohen_kappa(a, b))
        self.assertGreater(hi, hv.cohen_kappa(a, b))

    def test_summary_and_adjudication(self):
        from phishbench import human_validation as hv
        key = [{"item_id": f"RW-{i:03d}", "task": "RW", "sample_id": f"s{i}", "parent_id": f"p{i}", "generator": "g1" if i < 10 else "g2",
                "source": "EXT", "label": i % 2, "level": "L3", "cell": "c"} for i in range(20)] + \
              [{"item_id": "DN-001", "task": "DN", "sample_id": "d", "parent_id": "p", "generator": "g1", "source": "EXT",
                "label": 0, "level": "L4", "cell": "c"}]
        def rating(k, flip=False):
            if k["task"] == "DN":
                return {"item_id": k["item_id"], "task": "DN", "plausible_legitimate": "yes"}
            lab = hv.LABEL_NAME[k["label"]]
            if k["generator"] == "g2" and k["item_id"] in ("RW-010", "RW-011"):
                lab = "unsure"                       # g2 loses 2 of 10 -> 80% -> sensitivity only
            if flip and k["item_id"] == "RW-000":
                lab = "phishing"
            return {"item_id": k["item_id"], "task": "RW", "intent_preserved": "yes", "security_element_changed": "no", "rewrite_label": lab}
        ra, rb = [rating(k) for k in key], [rating(k, flip=True) for k in key]
        dis = hv.disagreements(ra, rb)
        self.assertEqual([(d["item_id"], d["question"]) for d in dis], [("RW-000", "rewrite_label")])
        with self.assertRaises(ValueError):
            hv.summarize(key, ra, rb, [])
        adj = [{**dis[0], "resolved": "legitimate"}]
        s = hv.summarize(key, ra, rb, adj, iterations=200)
        self.assertEqual(s["decisions"]["g1"]["rw_results_role"], "primary")
        self.assertEqual(s["decisions"]["g1"]["label_preservation"], 1.0)
        self.assertEqual(s["decisions"]["g2"]["rw_results_role"], "sensitivity_only")
        self.assertEqual(s["decisions"]["g2"]["label_preservation"], 0.8)
        self.assertEqual(s["n_disagreements"], 1)
        self.assertTrue(all("body" not in x and "subject" not in x for x in s["items"]))

    def test_practice_outside_sample(self):
        from phishbench import human_validation as hv
        gens, recs, parents = _hv_records()
        rw, dn, _ = hv.draw_sample(recs, gens, rw_per_stratum=4, dn_per_stratum=2, seed=1)
        base = [{"sample_id": pid, "parent_id": pid, "cell": pid.split(":")[0], "label": 0 if "legit" in pid else 1,
                 "subject": "s", "body": "b"} for pid in parents]
        d2 = [{"sample_id": f"d2:{pid}", "parent_id": pid, "cell": "IN-legit-L3-gpt4o" if "legit" in pid else "IN-phish-L3-gpt4o",
               "label": 0 if "legit" in pid else 1, "subject": "s", "body": "http://z.org"} for pid in parents if pid.startswith("IN-")]
        ai = [{"sample_id": f"{c}:{i}", "parent_id": f"{c}:{i}", "cell": c, "label": 0, "subject": "s", "body": "b"}
              for c in hv.PRACTICE_DN_CELLS for i in range(6)]
        items, key, rep = hv.draw_practice(base + d2 + ai, rw, dn, rw_per_label=3, dn_per_cell=2, seed=1)
        self.assertEqual(len(items), 3 * 2 + 2 * 2)
        self.assertTrue(all(r["drawn"] == r["target"] for r in rep))
        used = {r["native_id"] for r in rw}
        self.assertFalse({k["sample_id"].split("d2:")[-1] for k in key if k["task"] == "RW"} & used)
        self.assertTrue(all(x["item_id"].startswith("P-") for x in items))
        self.assertTrue(all("hxxp://" in x["body"] for x in items if x["task"] == "RW"))
        self.assertEqual(hv.draw_practice(list(reversed(base + d2 + ai)), rw, dn, 3, 2, 1)[1], key)

    @unittest.skipUnless(__import__("importlib").util.find_spec("openpyxl"), "openpyxl not installed")
    def test_workbook_roundtrip(self):
        from openpyxl import load_workbook
        from phishbench import human_validation as hv
        gens, recs, parents = _hv_records()
        rw, dn, _ = hv.draw_sample(recs, gens, rw_per_stratum=2, dn_per_stratum=1, seed=1)
        items, key = hv.make_items(rw, dn, parents, seed=1)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "A.xlsx"
            hv.write_workbook(p, hv.rater_order(items, "A", 1), "A")
            with self.assertRaises(ValueError):          # empty answers are rejected
                hv.read_workbook(p)
            wb = load_workbook(p)
            for task, qs in hv.QUESTIONS.items():
                ws = wb[task]
                hdr = [c.value for c in ws[1]]
                for row in ws.iter_rows(min_row=2):
                    for q, allowed in qs.items():
                        row[hdr.index(q)].value = allowed[0].upper()     # case is normalised
            wb.save(p)
            back = hv.read_workbook(p)
            self.assertEqual(sorted(r["item_id"] for r in back), sorted(x["item_id"] for x in items))
            self.assertTrue(all("body" not in r for r in back))
            self.assertEqual(back[0]["intent_preserved" if back[0]["task"] == "RW" else "plausible_legitimate"], "yes")
