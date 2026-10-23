"""
Stage 2: Active Anomaly Detector (TensorFlow Sequential Autoencoder)
===================================================================
Evaluates real-time in-game telemetry conditions during live matches.
Features are decided dynamically by the game developer (e.g. movement speed,
player height/elevation, active DPM, micro-aim adjustments, tick latency, etc.).

Key Design Specifications:
  1. Feature-Agnostic: Adapts to any real-time telemetry dimensionality.
  2. Deep Autoencoder Architecture: Trained on normal clean gameplay telemetry to
     reconstruct legitimate human movement patterns.
  3. Dynamic Anomaly Thresholds: Calibrates gray and red thresholds adaptively
     from baseline reconstruction error (MSE) distribution.
  4. Early GREEN Discard: Clean players are immediately dropped to minimize
     server CPU and memory overhead during high-frequency tick simulations.
     Reports only GRAY and RED.
  5. Independent Operation: Runs concurrently and independently from Stage 1.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
import os
import json
import logging
import numpy as np
import tensorflow as tf

from .scaler import FeatureScaler

logger = logging.getLogger("cds.active_anomaly")


class ActiveAnomalyDetector:
    """
    TensorFlow Sequential Deep Autoencoder for high-frequency in-game telemetry anomaly detection.
    """

    def __init__(
        self,
        input_dim: Optional[int] = None,
        gray_error_threshold: Optional[float] = None,
        red_error_threshold: Optional[float] = None,
        latent_dim: Optional[int] = None,
        learning_rate: float = 0.005,
        auto_scale: bool = True,
    ):
        """
        :param input_dim: Number of developer-defined telemetry features.
        :param gray_error_threshold: MSE error threshold above which telemetry is GRAY.
               If None, automatically calibrated to the 95th percentile of normal data.
        :param red_error_threshold: MSE error threshold above which telemetry is RED.
               If None, automatically calibrated to the 99th percentile of normal data.
        :param latent_dim: Latent representation bottleneck dimension.
        :param learning_rate: Adam optimizer learning rate.
        :param auto_scale: Automatically normalize features with FeatureScaler.
        """
        self.input_dim = input_dim
        self.gray_error_threshold = gray_error_threshold
        self.red_error_threshold = red_error_threshold
        self.latent_dim = latent_dim
        self.learning_rate = learning_rate
        self.auto_scale = auto_scale

        self.autoencoder: Optional[tf.keras.Sequential] = None
        self.scaler: Optional[FeatureScaler] = FeatureScaler(method="standard") if auto_scale else None
        self.is_trained: bool = False
        self.baseline_stats: Dict[str, float] = {}

        if input_dim is not None:
            self.build_model(input_dim)

    def build_model(self, input_dim: int) -> tf.keras.Sequential:
        """
        Constructs the Deep Autoencoder:
          - Input: Dynamic feature count (decided by developer)
          - Encoder: Compresses features into latent representation
          - Decoder: Reconstructs the input feature vector
        """
        self.input_dim = input_dim
        bottleneck = self.latent_dim or max(2, input_dim // 2)

        layers = [
            tf.keras.layers.Input(shape=(input_dim,)),
            # Encoder
            tf.keras.layers.Dense(max(16, input_dim * 2), activation="relu"),
            tf.keras.layers.Dense(max(8, bottleneck * 2), activation="relu"),
            tf.keras.layers.Dense(bottleneck, activation="relu"),
            # Decoder
            tf.keras.layers.Dense(max(8, bottleneck * 2), activation="relu"),
            tf.keras.layers.Dense(max(16, input_dim * 2), activation="relu"),
            tf.keras.layers.Dense(input_dim, activation="linear"),
        ]

        self.autoencoder = tf.keras.Sequential(layers)
        self.autoencoder.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss="mse",
        )
        logger.info("Stage 2 Autoencoder compiled with input_dim=%d, latent_dim=%d", input_dim, bottleneck)
        return self.autoencoder

    def train_baseline(
        self,
        X_clean: Union[np.ndarray, List[List[float]]],
        epochs: int = 35,
        batch_size: int = 16,
        calibrate_percentiles: Tuple[float, float] = (95.0, 99.0),
        verbose: int = 0,
    ) -> tf.keras.callbacks.History:
        """
        Calibrates the Autoencoder on legitimate, clean gameplay telemetry.
        Automatically derives gray and red MSE thresholds if not explicitly provided.
        """
        X = np.asarray(X_clean, dtype=np.float32)
        if len(X) == 0:
            raise ValueError("Telemetry baseline dataset X_clean cannot be empty.")

        if self.auto_scale and self.scaler is not None:
            X = self.scaler.fit_transform(X)

        if self.autoencoder is None or self.input_dim != X.shape[1]:
            self.build_model(input_dim=X.shape[1])

        history = self.autoencoder.fit(
            X,
            X,
            epochs=epochs,
            batch_size=batch_size,
            verbose=verbose,
        )
        self.is_trained = True

        # Compute baseline reconstruction errors to adaptively calibrate thresholds
        preds = self.autoencoder.predict(X, verbose=0)
        baseline_errors = np.mean(np.square(X - preds), axis=1)

        mean_err = float(np.mean(baseline_errors))
        std_err = float(np.std(baseline_errors))
        raw_p_gray = float(np.percentile(baseline_errors, calibrate_percentiles[0]))
        raw_p_red = float(np.percentile(baseline_errors, calibrate_percentiles[1]))

        # Safeguard: ensure minimum practical anomaly separation even on small baselines
        p_gray = max(raw_p_gray, 0.05)
        p_red = max(raw_p_red, p_gray * 2.5, 0.15)

        self.baseline_stats = {
            "mean_error": mean_err,
            "std_error": std_err,
            "p95_error": p_gray,
            "p99_error": p_red,
        }

        if self.gray_error_threshold is None:
            self.gray_error_threshold = round(p_gray, 5)
        if self.red_error_threshold is None:
            self.red_error_threshold = round(p_red, 5)

        logger.info(
            "Stage 2 Autoencoder calibrated. Baseline mean=%.5f, std=%.5f. Thresholds: GRAY=%.5f, RED=%.5f",
            mean_err,
            std_err,
            self.gray_error_threshold,
            self.red_error_threshold,
        )
        return history

    def compute_reconstruction_error(
        self,
        X: Union[np.ndarray, List[List[float]]],
    ) -> np.ndarray:
        """
        Computes Mean Squared Error (MSE) between live telemetry and its reconstruction.
        """
        if self.autoencoder is None or not self.is_trained:
            raise RuntimeError(
                "Autoencoder is not trained yet. Call .train_baseline(X_clean) first."
            )

        X_arr = np.asarray(X, dtype=np.float32)
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(1, -1)

        if self.auto_scale and self.scaler is not None:
            X_arr = self.scaler.transform(X_arr)

        preds = self.autoencoder.predict(X_arr, verbose=0)
        mse = np.mean(np.square(X_arr - preds), axis=1)
        return mse

    def evaluate_telemetry(
        self,
        X_live: Union[np.ndarray, List[List[float]]],
        player_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates real-time match telemetry.
        Behavior:
          - GREEN players (normal MSE) are REMOVED / DISCARDED immediately.
          - Reports ONLY GRAY and RED.
        """
        X_arr = np.asarray(X_live, dtype=np.float32)
        if X_arr.ndim == 1:
            X_arr = X_arr.reshape(1, -1)

        n_samples = X_arr.shape[0]
        if player_ids is None:
            pids = [f"player_{i}" for i in range(n_samples)]
        else:
            pids = list(player_ids)
            if len(pids) != n_samples:
                raise ValueError(f"Length of player_ids ({len(pids)}) does not match samples ({n_samples}).")

        errors = self.compute_reconstruction_error(X_arr)

        rosters: Dict[str, List[str]] = {"GRAY": [], "RED": []}
        details: List[Dict[str, Any]] = []
        discarded_green_count = 0

        for pid, err in zip(pids, errors):
            err_val = float(err)
            if err_val < self.gray_error_threshold:
                # Early discard optimization: dropped from memory/alerts
                discarded_green_count += 1
                continue
            elif err_val >= self.red_error_threshold:
                tier = "RED"
            else:
                tier = "GRAY"

            rosters[tier].append(pid)
            details.append({
                "player_id": pid,
                "tier": tier,
                "reconstruction_error": round(err_val, 5),
                "threshold_applied": self.red_error_threshold if tier == "RED" else self.gray_error_threshold,
            })

        return {
            "rosters": rosters,
            "details": details,
            "discarded_green_count": discarded_green_count,
            "total_evaluated": n_samples,
        }

    def save(self, directory_path: str) -> None:
        """Saves Autoencoder model and calibration states."""
        os.makedirs(directory_path, exist_ok=True)
        if self.autoencoder is not None:
            self.autoencoder.save(os.path.join(directory_path, "active_anomaly_model.keras"))

        meta = {
            "input_dim": self.input_dim,
            "gray_error_threshold": self.gray_error_threshold,
            "red_error_threshold": self.red_error_threshold,
            "latent_dim": self.latent_dim,
            "learning_rate": self.learning_rate,
            "auto_scale": self.auto_scale,
            "is_trained": self.is_trained,
            "baseline_stats": self.baseline_stats,
            "scaler": self.scaler.to_dict() if self.scaler is not None else None,
        }
        with open(os.path.join(directory_path, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    @classmethod
    def load(cls, directory_path: str) -> "ActiveAnomalyDetector":
        """Loads trained Autoencoder and calibration states."""
        meta_path = os.path.join(directory_path, "metadata.json")
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        detector = cls(
            input_dim=meta["input_dim"],
            gray_error_threshold=meta["gray_error_threshold"],
            red_error_threshold=meta["red_error_threshold"],
            latent_dim=meta["latent_dim"],
            learning_rate=meta["learning_rate"],
            auto_scale=meta["auto_scale"],
        )

        model_path = os.path.join(directory_path, "active_anomaly_model.keras")
        if os.path.exists(model_path):
            detector.autoencoder = tf.keras.models.load_model(model_path)
            detector.is_trained = meta.get("is_trained", True)

        detector.baseline_stats = meta.get("baseline_stats", {})
        if meta.get("scaler") is not None:
            detector.scaler = FeatureScaler.from_dict(meta["scaler"])

        return detector
