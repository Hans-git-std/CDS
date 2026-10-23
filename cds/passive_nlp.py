"""
Stage 1: Passive NLP Detector (TensorFlow Sequential Model)
------------------------------------------------------------
Evaluates player statistics from the game database.
Features are decided by the developer (e.g. Win Rate, KD, Matches, Headshot %, DPM, etc.).
Uses a TensorFlow Sequential model with pre-configured activations.
Trained in cold-start mode using binary ground-truth: GREEN (0) and RED (1).
Outputs tri-state classifications: GREEN, GRAY, and RED.
"""

from typing import List, Dict, Any, Optional, Union
import numpy as np
import tensorflow as tf


class PassiveNLPDetector:
    def __init__(
        self,
        input_dim: Optional[int] = None,
        gray_threshold_low: float = 0.35,
        gray_threshold_high: float = 0.75,
    ):
        """
        Initializes the Stage 1 Passive NLP Detector.
        :param input_dim: Number of developer-defined features (e.g. 4, 10, 25).
        :param gray_threshold_low: Score below which player is GREEN (Clean).
        :param gray_threshold_high: Score above which player is RED (Cheater).
        Scores between [gray_threshold_low, gray_threshold_high] are marked GRAY (Suspicious).
        """
        self.input_dim = input_dim
        self.gray_threshold_low = gray_threshold_low
        self.gray_threshold_high = gray_threshold_high
        self.model: Optional[tf.keras.Sequential] = None
        self.is_trained: bool = False

        if input_dim is not None:
            self.build_model(input_dim)

    def build_model(self, input_dim: int) -> tf.keras.Sequential:
        """
        Defines the TensorFlow Sequential Model for historical feature classification.
        Architecture:
          - Input: Dynamic feature dimension (decided by developer)
          - Dense(64, activation='relu')
          - Dropout(0.2)
          - Dense(32, activation='relu')
          - Dense(1, activation='sigmoid') -> Continuous Risk Score [0.0 to 1.0]
        """
        self.input_dim = input_dim
        self.model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(input_dim,)),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid'),
        ])

        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.01),
            loss='binary_crossentropy',
            metrics=['accuracy'],
        )
        return self.model

    def train(
        self,
        X_train: Union[np.ndarray, List[List[float]]],
        y_train: Union[np.ndarray, List[int]],
        epochs: int = 15,
        batch_size: int = 16,
        verbose: int = 0,
    ) -> tf.keras.callbacks.History:
        """
        Cold-Start Training Mode:
        Developer provides ground-truth Answer Key with binary labels:
          - 0 for GREEN (Verified legitimate players)
          - 1 for RED (Confirmed banned cheaters)
        (In ground truth training, there is no mid-tier GRAY).
        """
        X = np.asarray(X_train, dtype=np.float32)
        y = np.asarray(y_train, dtype=np.float32)

        if self.model is None or self.input_dim != X.shape[1]:
            self.build_model(input_dim=X.shape[1])

        history = self.model.fit(
            X,
            y,
            epochs=epochs,
            batch_size=batch_size,
            verbose=verbose,
        )
        self.is_trained = True
        return history

    def predict_risk(self, X: Union[np.ndarray, List[List[float]]]) -> np.ndarray:
        """
        Computes continuous risk probabilities in [0.0, 1.0] for developer feature inputs.
        """
        if self.model is None or not self.is_trained:
            raise RuntimeError(
                "Model has not been trained yet. Please call .train(X_train, y_train) "
                "with your ground-truth Answer Key first."
            )
        X_arr = np.asarray(X, dtype=np.float32)
        preds = self.model.predict(X_arr, verbose=0)
        return preds.flatten()

    def classify(
        self,
        X: Union[np.ndarray, List[List[float]]],
        player_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Classifies players into GREEN, GRAY, and RED lists based on pre-decided thresholds:
          - Score < gray_threshold_low  -> GREEN
          - Score >= gray_threshold_high -> RED
          - Intermediate                 -> GRAY
        """
        X_arr = np.asarray(X, dtype=np.float32)
        n_samples = X_arr.shape[0]

        if player_ids is None:
            pids = [f"player_{i}" for i in range(n_samples)]
        else:
            pids = list(player_ids)

        risk_scores = self.predict_risk(X_arr)

        rosters = {"GREEN": [], "GRAY": [], "RED": []}
        details = []

        for pid, score in zip(pids, risk_scores):
            score_val = float(score)
            if score_val < self.gray_threshold_low:
                tier = "GREEN"
            elif score_val >= self.gray_threshold_high:
                tier = "RED"
            else:
                tier = "GRAY"

            rosters[tier].append(pid)
            details.append({
                "player_id": pid,
                "tier": tier,
                "risk_score": round(score_val, 4),
            })

        return {
            "rosters": rosters,
            "details": details,
        }

    def save_model(self, filepath: str) -> None:
        """Saves trained TensorFlow model to disk."""
        if self.model is not None:
            self.model.save(filepath)

    def load_model(self, filepath: str) -> None:
        """Loads saved TensorFlow model from disk."""
        self.model = tf.keras.models.load_model(filepath)
        self.is_trained = True
        self.input_dim = self.model.input_shape[-1]
