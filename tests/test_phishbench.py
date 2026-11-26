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
