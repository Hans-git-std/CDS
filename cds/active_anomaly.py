"""
Stage 2: Active Anomaly Detector (TensorFlow Sequential Autoencoder)
-------------------------------------------------------------------
Evaluates real-time in-game telemetry during live matches.
Features are decided by the developer (e.g. movement speed, player height, DPM,
aim adjustments, tick rates, etc.).
Uses a TensorFlow Sequential Autoencoder to learn normal gameplay patterns.
Reconstruction Error (MSE) identifies anomalous behaviors:
  - Clean players (GREEN) are discarded immediately to save compute.
  - Reports only GRAY (Suspicious) and RED (Critical Anomaly).
Both Stage 1 and Stage 2 run independently.
"""

from typing import List, Dict, Any, Optional, Union
import numpy as np
import tensorflow as tf


class ActiveAnomalyDetector:
    def __init__(
        self,
        input_dim: Optional[int] = None,
        gray_error_threshold: float = 0.08,
        red_error_threshold: float = 0.25,
    ):
        """
        Initializes the Stage 2 Active Anomaly Detector.
        :param input_dim: Number of developer-defined real-time telemetry features.
        :param gray_error_threshold: Reconstruction error (MSE) above which player is GRAY.
        :param red_error_threshold: Reconstruction error (MSE) above which player is RED.
        Errors below gray_error_threshold are GREEN (Clean) and removed immediately.
        """
        self.input_dim = input_dim
        self.gray_error_threshold = gray_error_threshold
        self.red_error_threshold = red_error_threshold
        self.autoencoder: Optional[tf.keras.Sequential] = None
        self.is_trained: bool = False

        if input_dim is not None:
            self.build_model(input_dim)

    def build_model(self, input_dim: int) -> tf.keras.Sequential:
        """
        Defines the TensorFlow Sequential Deep Autoencoder.
        Encoder compresses features down to an 8-dimension bottleneck;
        Decoder reconstructs the original feature vector.
        """
        self.input_dim = input_dim
        self.autoencoder = tf.keras.Sequential([
            # Input
            tf.keras.layers.Input(shape=(input_dim,)),
            # Encoder
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(8, activation='relu'),
            # Decoder
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(input_dim, activation='linear'),
        ])

        self.autoencoder.compile(
            optimizer='adam',
            loss='mse',
        )
        return self.autoencoder

    def train_baseline(
        self,
        X_clean: Union[np.ndarray, List[List[float]]],
        epochs: int = 15,
        batch_size: int = 16,
        verbose: int = 0,
    ) -> tf.keras.callbacks.History:
        """
        Trains the Autoencoder on legitimate, clean gameplay telemetry.
        The model learns the low-dimensional manifold of natural human gameplay.
        """
        X = np.asarray(X_clean, dtype=np.float32)

        if self.autoencoder is None or self.input_dim != X.shape[1]:
            self.build_model(input_dim=X.shape[1])

        # Autoencoder input equals target (self-reconstruction)
        history = self.autoencoder.fit(
            X,
            X,
            epochs=epochs,
            batch_size=batch_size,
            verbose=verbose,
        )
        self.is_trained = True
        return history

    def compute_reconstruction_error(
        self,
        X: Union[np.ndarray, List[List[float]]],
    ) -> np.ndarray:
        """
        Computes Mean Squared Error (MSE) between original features and reconstructed features.
        """
        if self.autoencoder is None or not self.is_trained:
            raise RuntimeError(
                "Autoencoder has not been trained yet. Please call .train_baseline(X_clean) first."
            )
        X_arr = np.asarray(X, dtype=np.float32)
        X_pred = self.autoencoder.predict(X_arr, verbose=0)
        # Mean Squared Error across feature dimensions per sample
        mse = np.mean(np.square(X_arr - X_pred), axis=1)
        return mse

    def evaluate_telemetry(
        self,
        X_live: Union[np.ndarray, List[List[float]]],
        player_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates real-time match telemetry.
        Behavior:
          - GREEN players (error < gray_error_threshold) are REMOVED / DISCARDED.
          - Reports ONLY GRAY and RED.
        """
        X_arr = np.asarray(X_live, dtype=np.float32)
        n_samples = X_arr.shape[0]

        if player_ids is None:
            pids = [f"player_{i}" for i in range(n_samples)]
        else:
            pids = list(player_ids)

        errors = self.compute_reconstruction_error(X_arr)

        rosters = {"GRAY": [], "RED": []}
        details = []
        discarded_green_count = 0

        for pid, err in zip(pids, errors):
            err_val = float(err)
            if err_val < self.gray_error_threshold:
                # Actively remove GREEN from alerts
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
            })

        return {
            "rosters": rosters,
            "details": details,
            "discarded_green_count": discarded_green_count,
        }

    def save_model(self, filepath: str) -> None:
        """Saves trained Autoencoder to disk."""
        if self.autoencoder is not None:
            self.autoencoder.save(filepath)

    def load_model(self, filepath: str) -> None:
        """Loads saved Autoencoder from disk."""
        self.autoencoder = tf.keras.models.load_model(filepath)
        self.is_trained = True
        self.input_dim = self.autoencoder.input_shape[-1]
