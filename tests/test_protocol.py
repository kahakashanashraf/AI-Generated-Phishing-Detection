import unittest
import pandas as pd
from src.audit import audit
from src.baseline import run

def sample():
    rows = []
    for gen, label in [("human", 0), ("model_a", 1), ("model_b", 1)]:
        for j in range(30):
            rows.append({"text": f"{gen} distinct sequence {j} action requested source specific phrase {gen}",
                         "label": label, "generator": gen, "source": gen,
                         "group_id": f"{gen}-{j}"})
    return pd.DataFrame(rows)

class ProtocolTests(unittest.TestCase):
    def test_reject_duplicate_cross_group(self):
        df = sample()
        df.loc[1, "text"] = df.loc[0, "text"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit(df)
    def test_reject_generator_group_leakage(self):
        df = sample()
        df.loc[df.generator.eq("model_b"), "group_id"] = [
            f"model_a-{j}" for j in range(30)
        ]
        with self.assertRaisesRegex(ValueError, "ancestor"):
            run(df, "model_b")
    def test_reject_label_mismatch(self):
        df = sample()
        df.loc[0, "generator"] = "model_a"
        with self.assertRaisesRegex(ValueError, "Human label"):
            audit(df)
    def test_heldout_has_no_training_samples(self):
        out = run(sample(), "model_b")
        self.assertNotIn("model_b", out["seen_train_generators"])
        self.assertEqual(out["unseen_ai_test_n"], 30)
        self.assertEqual(out["threshold_source"], "seen_validation_only")

if __name__ == "__main__":
    unittest.main()
