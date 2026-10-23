"""
Stage 1: Passive Detector (TensorFlow Sequential Classifier)
============================================================
Evaluates historical player statistics from the game database.
Features are decided dynamically by the game developer (e.g. win rate, KD ratio,
headshot percentage, damage per match, account lifetime, etc.).

Key Design Specifications:
  1. Feature-Agnostic: Adapts to any input dimensionality chosen by the developer.
  2. Powered by TensorFlow: Uses tf.keras.Sequential with pre-configured activations.
  3. Cold-Start Training Mode: Trained on developer-provided ground-truth Answer Key:
     - 0 = GREEN (Clean verified players)
     - 1 = RED (Confirmed banned cheaters)
     (In ground truth training, there is NO intermediate GRAY).
  4. Tri-State Live Classification: Outputs GREEN (clean), GRAY (suspicious), and RED (cheater).
"""

from typing import List, Dict, Any, Optional, Union, Tuple
import os
import json
import logging
import numpy as np
import tensorflow as tf

from .scaler import FeatureScaler

logger = logging.getLogger("cds.passive_nlp")


class PassiveNLPDetector:
    """
    High-performance TensorFlow Sequential classifier for historical game database telemetry.

    Architecture (5-Layer Sequential Neural Network as specified by CDS design):
      - Layer 1: Input / Feature Projection Dense Layer (input_dim units, ReLU)
                 [Guidance: 64 to 128 historical features recommended for game developers]
      - Layer 2 (Mid 1): Dense(input_dim // 2 units, ReLU)
      - Layer 3 (Mid 2): Dense(input_dim // 2 units, ReLU)
      - Layer 4 (Mid 3): Dense(input_dim // 4 units, ReLU)
      - Layer 5 (Output): Dense(1 unit, Sigmoid) -> Continuous Cheat Probability [0.0 to 1.0]
    """

    def __init__(
        self,
        input_dim: Optional[int] = None,
        gray_threshold_low: float = 0.35,
        gray_threshold_high: float = 0.75,
        hidden_units: Optional[Tuple[int, ...]] = None,
        dropout_rate: float = 0.15,
        learning_rate: float = 0.01,
        auto_scale: bool = True,
    ):
        """
        :param input_dim: Number of developer-defined features (recommended: 64 to 128).
        :param gray_threshold_low: Risk score threshold below which player is GREEN (Clean).
        :param gray_threshold_high: Risk score threshold above which player is RED (Cheater).
               Scores in [gray_threshold_low, gray_threshold_high] are marked GRAY (Suspicious).
        :param hidden_units: Optional custom tuple of neuron counts. If None, uses the standard
               5-layer CDS design: [input_dim, input_dim // 2, input_dim // 2, input_dim // 4, 1].
        :param dropout_rate: Regularization dropout probability.
        :param learning_rate: Adam optimizer learning rate.
        :param auto_scale: Whether to automatically fit and transform features with FeatureScaler.
        """
        self.input_dim = input_dim
        self.gray_threshold_low = gray_threshold_low
        self.gray_threshold_high = gray_threshold_high
        self.hidden_units = hidden_units
        self.dropout_rate = dropout_rate
        self.learning_rate = learning_rate
        self.auto_scale = auto_scale

        self.model: Optional[tf.keras.Sequential] = None
        self.scaler: Optional[FeatureScaler] = FeatureScaler(method="minmax") if auto_scale else None
        self.is_trained: bool = False

        if input_dim is not None:
            self.build_model(input_dim)

    def build_model(self, input_dim: int) -> tf.keras.Sequential:
        """
        Defines the 5-layer TensorFlow Sequential Model for historical feature classification:
          - Layer 1: Dense(units=input_dim, activation='relu') [Guide: 64-128 features recommended]
          - Layer 2 (Mid 1): Dense(units=input_dim // 2, activation='relu')
          - Layer 3 (Mid 2): Dense(units=input_dim // 2, activation='relu')
          - Layer 4 (Mid 3): Dense(units=input_dim // 4, activation='relu')
          - Layer 5 (Output): Dense(units=1, activation='sigmoid') -> Continuous Risk Score [0.0 to 1.0]
        """
        self.input_dim = input_dim

        # Calculate neuron counts following the 5-layer CDS specification
        if self.hidden_units is not None:
            units_list = list(self.hidden_units)
        else:
            # Standard 5-layer CDS design:
            # Layer 1: input_dim (guided 64 to 128 for developers; floor of 64 provides capacity for toy feature sets)
            # Layer 2 (Mid 1): input // 2
            # Layer 3 (Mid 2): input // 2
            # Layer 4 (Mid 3): input // 4
            # Layer 5 (Output): 1 (sigmoid)
            base_dim = max(int(input_dim), 64)
            l1_units = base_dim
            l2_units = max(int(base_dim // 2), 32)
            l3_units = max(int(base_dim // 2), 32)
            l4_units = max(int(base_dim // 4), 16)
            units_list = [l1_units, l2_units, l3_units, l4_units]

        layers = [
            tf.keras.layers.Input(shape=(input_dim,)),
            tf.keras.layers.Dense(units_list[0], activation="relu", name="dense_l1_input_project"),
        ]

        if self.dropout_rate > 0.0:
            layers.append(tf.keras.layers.Dropout(self.dropout_rate, name="dropout_1"))

        # Mid layers 2, 3, 4
        for idx, units in enumerate(units_list[1:], start=2):
            layers.append(tf.keras.layers.Dense(units, activation="relu", name=f"dense_l{idx}_mid"))

        # Layer 5: Output layer with Sigmoid activation for binary risk probability
        layers.append(tf.keras.layers.Dense(1, activation="sigmoid", name="dense_l5_output_risk"))

        self.model = tf.keras.Sequential(layers, name="cds_stage1_passive_nlp")
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )
        logger.info(
            "Stage 1 5-Layer TensorFlow model compiled with input_dim=%d, layers=%s, output=1",
            input_dim,
            units_list,
        )
        return self.model

    def train(
        self,
        X_train: Union[np.ndarray, List[List[float]]],
        y_train: Union[np.ndarray, List[int]],
        epochs: int = 40,
        batch_size: int = 16,
        patience: int = 5,
        verbose: int = 0,
    ) -> tf.keras.callbacks.History:
        """
        Cold-Start Training Mode:
        Developer provides ground-truth Answer Key with binary labels:
          - 0 for GREEN (Verified legitimate accounts)
          - 1 for RED (Confirmed banned cheaters)
        (In ground truth training, there is NO intermediate GRAY).
        """
        X = np.asarray(X_train, dtype=np.float32)
        y = np.asarray(y_train, dtype=np.float32).flatten()

        if len(X) == 0:
            raise ValueError("Training dataset X_train cannot be empty.")
        if len(X) != len(y):
            raise ValueError(f"Feature count {len(X)} does not match label count {len(y)}.")

        unique_labels = set(np.unique(y).astype(int))
        if not unique_labels.issubset({0, 1}):
            raise ValueError(
                f"Ground-truth labels must be binary 0 (GREEN) and 1 (RED). Found: {unique_labels}"
            )

        if self.auto_scale and self.scaler is not None:
            X = self.scaler.fit_transform(X)

        if self.model is None or self.input_dim != X.shape[1]:
            self.build_model(input_dim=X.shape[1])

        callbacks = []
        if patience > 0 and epochs > 10:
            callbacks.append(
                tf.keras.callbacks.EarlyStopping(
                    monitor="loss", patience=patience, restore_best_weights=True
                )
            )

        history = self.model.fit(
            X,
            y,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=verbose,
        )
        self.is_trained = True
        logger.info(
            "Stage 1 model training complete (%d samples, %d epochs).", len(X), len(history.history["loss"])
        )
        return history

    def predict_risk(self, X: Union[np.ndarray, List[List[float]]]) -> np.ndarray:
        """
        Returns continuous risk probabilities in [0.0, 1.0] for developer-defined features.
        """
        if self.model is None or not self.is_trained:
            raise RuntimeError(
                "Model has not been trained yet. Please call .train(X_train, y_train) with your Answer Key."
            )

        X_arr = np.asarray(X, dtype=np.float32)
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(1, -1)

        if self.auto_scale and self.scaler is not None:
            X_arr = self.scaler.transform(X_arr)

        preds = self.model.predict(X_arr, verbose=0)
        return preds.flatten()

    def classify(
        self,
        X: Union[np.ndarray, List[List[float]]],
        player_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Classifies players into GREEN, GRAY, and RED rosters.
        """
        X_arr = np.asarray(X, dtype=np.float32)
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(1, -1)

        n_samples = X_arr.shape[0]
        if player_ids is None:
            pids = [f"player_{i}" for i in range(n_samples)]
        else:
            pids = list(player_ids)
            if len(pids) != n_samples:
                raise ValueError(f"Length of player_ids ({len(pids)}) does not match samples ({n_samples}).")

        risk_scores = self.predict_risk(X_arr)

        rosters: Dict[str, List[str]] = {"GREEN": [], "GRAY": [], "RED": []}
        details: List[Dict[str, Any]] = []

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

    def save(self, directory_path: str) -> None:
        """Saves TensorFlow model and scaler state to directory."""
        os.makedirs(directory_path, exist_ok=True)
        if self.model is not None:
            model_path = os.path.join(directory_path, "passive_nlp_model.keras")
            self.model.save(model_path)

        meta = {
            "input_dim": self.input_dim,
            "gray_threshold_low": self.gray_threshold_low,
            "gray_threshold_high": self.gray_threshold_high,
            "hidden_units": list(self.hidden_units) if self.hidden_units is not None else None,
            "dropout_rate": self.dropout_rate,
            "learning_rate": self.learning_rate,
            "auto_scale": self.auto_scale,
            "is_trained": self.is_trained,
            "scaler": self.scaler.to_dict() if self.scaler is not None else None,
        }
        with open(os.path.join(directory_path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    @classmethod
    def load(cls, directory_path: str) -> "PassiveNLPDetector":
        """Loads trained detector and scaler state from directory."""
        meta_path = os.path.join(directory_path, "metadata.json")
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        hidden_units_val = tuple(meta["hidden_units"]) if meta.get("hidden_units") is not None else None
        detector = cls(
            input_dim=meta["input_dim"],
            gray_threshold_low=meta["gray_threshold_low"],
            gray_threshold_high=meta["gray_threshold_high"],
            hidden_units=hidden_units_val,
            dropout_rate=meta["dropout_rate"],
            learning_rate=meta["learning_rate"],
            auto_scale=meta["auto_scale"],
        )

        model_path = os.path.join(directory_path, "passive_nlp_model.keras")
        if os.path.exists(model_path):
            detector.model = tf.keras.models.load_model(model_path)
            detector.is_trained = meta.get("is_trained", True)

        if meta.get("scaler") is not None:
            detector.scaler = FeatureScaler.from_dict(meta["scaler"])

        return detector
