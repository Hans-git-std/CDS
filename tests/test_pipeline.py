"""
Unit Test Suite for CDS (Cheat Detection System)
================================================
Tests FeatureScaler, PassiveNLPDetector, ActiveAnomalyDetector,
AgenticProfileInspector, and PipelineOrchestrator.
"""

import unittest
import numpy as np
import tempfile
import shutil

from cds import (
    FeatureScaler,
    PassiveNLPDetector,
    ActiveAnomalyDetector,
    AgenticProfileInspector,
    PipelineOrchestrator,
)


class TestFeatureScaler(unittest.TestCase):
    def test_minmax_scaler(self):
        X = np.array([[10.0, 100.0], [20.0, 200.0], [30.0, 300.0]], dtype=np.float32)
        scaler = FeatureScaler(method="minmax")
        X_scaled = scaler.fit_transform(X)

        self.assertAlmostEqual(float(X_scaled[0, 0]), 0.0)
        self.assertAlmostEqual(float(X_scaled[2, 0]), 1.0)
        self.assertAlmostEqual(float(X_scaled[1, 1]), 0.5)

    def test_serialization(self):
        X = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        scaler = FeatureScaler(method="minmax")
        scaler.fit(X)
        data = scaler.to_dict()

        restored = FeatureScaler.from_dict(data)
        self.assertTrue(restored.is_fitted)
        transformed = restored.transform([[2.0, 3.0]])
        self.assertAlmostEqual(float(transformed[0, 0]), 0.5)


class TestPassiveNLPDetector(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_train_and_classify(self):
        # Developer provides arbitrary features: 3 features
        clean = [[0.05, 0.10, 0.15], [0.08, 0.12, 0.18], [0.03, 0.07, 0.10]] * 5
        red = [[0.90, 0.95, 0.92], [0.88, 0.92, 0.96], [0.95, 0.98, 0.90]] * 5
        X_train = clean + red
        y_train = [0] * len(clean) + [1] * len(red)

        detector = PassiveNLPDetector(auto_scale=True)
        detector.train(X_train, y_train, epochs=30, verbose=0)
        self.assertTrue(detector.is_trained)

        # Test live classification
        X_test = [[0.04, 0.08, 0.12], [0.95, 0.96, 0.94]]
        results = detector.classify(X_test, player_ids=["clean_p", "hacker_p"])

        self.assertIn("clean_p", results["rosters"]["GREEN"])
        self.assertIn("hacker_p", results["rosters"]["RED"])

    def test_save_and_load(self):
        clean = [[0.1, 0.2]] * 10
        red = [[0.9, 0.8]] * 10
        detector = PassiveNLPDetector()
        detector.train(clean + red, [0] * 10 + [1] * 10, epochs=15, verbose=0)

        detector.save(self.temp_dir)
        loaded = PassiveNLPDetector.load(self.temp_dir)
        self.assertTrue(loaded.is_trained)
        pred = loaded.predict_risk([[0.1, 0.2]])
        self.assertTrue(len(pred) == 1)


class TestActiveAnomalyDetector(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_autoencoder_and_early_green_drop(self):
        # Developer telemetry: 4 features
        clean_telem = np.random.normal(0.2, 0.02, (60, 4)).astype(np.float32)
        detector = ActiveAnomalyDetector(auto_scale=True)
        detector.train_baseline(clean_telem, epochs=30, verbose=0)

        # Normal telemetry vs extreme exploit
        normal_sample = np.array([[0.20, 0.21, 0.19, 0.20]], dtype=np.float32)
        extreme_exploit = np.array([[5.0, 9.0, 8.0, 7.0]], dtype=np.float32)

        X_eval = np.vstack([normal_sample, extreme_exploit])
        res = detector.evaluate_telemetry(X_eval, player_ids=["clean_telemetry", "speedhacker"])

        # Clean player must be discarded immediately
        self.assertEqual(res["discarded_green_count"], 1)
        # Exploit must be reported in RED or GRAY
        self.assertIn("speedhacker", res["rosters"]["RED"])


class TestAgenticProfileInspector(unittest.TestCase):
    def test_seller_detection(self):
        inspector = AgenticProfileInspector()

        # Cheat seller with contact handle
        res_seller = inspector.inspect_text("VIP Undetected Cheat available. Add t.me/fast_hacks")
        self.assertEqual(res_seller["tier"], "GRAY")
        self.assertGreaterEqual(res_seller["suspicion_score"], 0.40)

        # Clean text
        res_clean = inspector.inspect_text("Good game, having fun with squad!")
        self.assertEqual(res_clean["tier"], "GREEN")

    def test_safety_invariant_never_red(self):
        inspector = AgenticProfileInspector()
        # Even blatant text must NEVER be RED directly
        res = inspector.inspect_text("BUY AIMBOT AND ESP NOW DISCORD.GG/HACKS DM FOR VIP SCRIPT")
        self.assertNotEqual(res["tier"], "RED")
        self.assertEqual(res["tier"], "GRAY")


class TestPipelineOrchestrator(unittest.TestCase):
    def test_consensus_rules(self):
        orchestrator = PipelineOrchestrator()

        player_ids = ["P_Clean", "P_Borderline", "P_TripleGray", "P_DirectRed"]

        s1_rosters = {
            "GREEN": ["P_Clean", "P_Borderline"],
            "GRAY": ["P_TripleGray"],
            "RED": ["P_DirectRed"],
        }
        s2_rosters = {
            "GRAY": ["P_Borderline", "P_TripleGray"],
            "RED": [],
        }
        s3_rosters = {
            "GREEN": ["P_Clean"],
            "GRAY": ["P_Borderline", "P_TripleGray"],
        }

        verdict = orchestrator.harmonize_rosters(
            all_player_ids=player_ids,
            stage1_rosters=s1_rosters,
            stage2_rosters=s2_rosters,
            stage3_rosters=s3_rosters,
        )

        rosters = verdict["rosters"]
        # P_Clean: Clean in all -> GREEN
        self.assertIn("P_Clean", rosters["GREEN"])
        # P_Borderline: GRAY in S2 + S3 (2 GRAYs) -> retained in GRAY
        self.assertIn("P_Borderline", rosters["GRAY"])
        # P_TripleGray: GRAY in S1 + S2 + S3 (3 GRAYs) -> PROMOTED TO RED!
        self.assertIn("P_TripleGray", rosters["RED"])
        # P_DirectRed: Direct RED from Stage 1 -> RED
        self.assertIn("P_DirectRed", rosters["RED"])


if __name__ == "__main__":
    unittest.main()
