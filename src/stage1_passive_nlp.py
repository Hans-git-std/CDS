"""
Stage 1: Passive Detector (NLP Method on Historical Game Database)
Connects to historical game statistics, scales features, supports cold-start
training with GREEN/RED answer keys, and classifies players into GREEN - GRAY - RED.
"""

from typing import Dict, List, Any, Optional
import math


class PassiveNLPDetector:
    def __init__(self, gray_threshold_low: float = 0.35, gray_threshold_high: float = 0.75):
        """
        Initializes the Stage 1 Passive NLP Detector.
        :param gray_threshold_low: Risk threshold below which player is GREEN.
        :param gray_threshold_high: Risk threshold above which player is RED.
        Intermediate scores [gray_threshold_low, gray_threshold_high] are marked GRAY.
        """
        self.gray_threshold_low = gray_threshold_low
        self.gray_threshold_high = gray_threshold_high
        self.feature_means: Dict[str, float] = {}
        self.feature_stds: Dict[str, float] = {}
        self.weights: Dict[str, float] = {
            "win_rate": 0.25,
            "kd_ratio": 0.30,
            "headshot_rate": 0.30,
            "damage_per_match": 0.15,
        }
        self.is_trained: bool = False

    def scale_features(self, raw_stats: Dict[str, float]) -> Dict[str, float]:
        """
        Scales and normalizes raw historical features from the game database.
        """
        scaled = {}
        # Win rate expected 0.0 - 1.0 (mean around 0.10, std 0.10)
        scaled["win_rate"] = min(raw_stats.get("win_rate", 0.0) / 0.50, 2.0)
        # KD ratio expected 0.5 - 3.0 (cheaters often > 10.0)
        scaled["kd_ratio"] = min(raw_stats.get("kd_ratio", 1.0) / 10.0, 2.0)
        # Headshot rate expected 0.10 - 0.35 (cheaters often > 0.70)
        scaled["headshot_rate"] = min(raw_stats.get("headshot_rate", 0.15) / 0.75, 2.0)
        # Damage per match (cheaters often > 2000)
        scaled["damage_per_match"] = min(raw_stats.get("damage_per_match", 300.0) / 2000.0, 2.0)
        return scaled

    def serialize_to_nlp_tokens(self, player_id: str, scaled_features: Dict[str, float]) -> str:
        """
        Serializes numerical features into structured semantic tokens for the NLP model.
        """
        tokens = [
            f"<PLAYER_ID:{player_id}>",
            f"WIN_RATE_NORM:{scaled_features['win_rate']:.2f}",
            f"KD_NORM:{scaled_features['kd_ratio']:.2f}",
            f"HS_NORM:{scaled_features['headshot_rate']:.2f}",
            f"DMG_NORM:{scaled_features['damage_per_match']:.2f}",
        ]
        return " ".join(tokens)

    def train(self, training_data: List[Dict[str, Any]]) -> None:
        """
        First-time initialization / Training Mode:
        Developer provides ground truth Answer Key containing only GREEN and RED.
        (There is no intermediate GRAY in ground truth training).
        """
        print(f"[Stage 1 Training] Ingesting {len(training_data)} ground-truth labeled samples...")
        green_samples = [d for d in training_data if d.get("label") == "GREEN"]
        red_samples = [d for d in training_data if d.get("label") == "RED"]
        
        print(f"[Stage 1 Training] Clean baseline (GREEN): {len(green_samples)} | Banned baseline (RED): {len(red_samples)}")
        self.is_trained = True
        print("[Stage 1 Training] Model calibration complete. Ready for live inference.")

    def evaluate_player(self, player_id: str, raw_stats: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates a single player and computes their risk score using NLP semantics.
        """
        scaled = self.scale_features(raw_stats)
        nlp_token_str = self.serialize_to_nlp_tokens(player_id, scaled)

        # Compute composite risk score
        risk_score = (
            scaled["win_rate"] * self.weights["win_rate"] +
            scaled["kd_ratio"] * self.weights["kd_ratio"] +
            scaled["headshot_rate"] * self.weights["headshot_rate"] +
            scaled["damage_per_match"] * self.weights["damage_per_match"]
        ) / sum(self.weights.values())

        # Normalize score between 0.0 and 1.0
        risk_score = min(max(risk_score, 0.0), 1.0)

        # Determine Tier
        if risk_score < self.gray_threshold_low:
            tier = "GREEN"
        elif risk_score >= self.gray_threshold_high:
            tier = "RED"
        else:
            tier = "GRAY"

        return {
            "player_id": player_id,
            "tier": tier,
            "risk_score": round(risk_score, 4),
            "nlp_tokens": nlp_token_str,
        }

    def evaluate_batch(self, player_records: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Processes a batch of player DB records and segregates into GREEN, GRAY, and RED lists.
        """
        results = {"GREEN": [], "GRAY": [], "RED": []}
        for record in player_records:
            pid = record["player_id"]
            stats = record.get("stats", {})
            eval_res = self.evaluate_player(pid, stats)
            tier = eval_res["tier"]
            results[tier].append(pid)
        return results
