"""
Feature Scaling & Preprocessing Utilities for CDS
-------------------------------------------------
Provides robust normalization (MinMax, Standard Z-score, Robust Percentile)
for arbitrary developer-defined feature matrices.
Handles missing/NaN values and serializes scaler states.
"""

from typing import Union, List, Optional, Dict, Any
import numpy as np


class FeatureScaler:
    """
    Robust feature scaler supporting dynamic developer feature arrays.
    Methods:
      - 'minmax'  : Scales features to [0.0, 1.0]
      - 'standard': Standardizes features (zero mean, unit variance)
      - 'robust'  : Scales using median and interquartile range (IQR)
    """

    def __init__(self, method: str = "minmax", clip_range: Optional[tuple] = None):
        if method not in ("minmax", "standard", "robust"):
            raise ValueError(f"Unknown scaling method '{method}'. Choose 'minmax', 'standard', or 'robust'.")
        self.method = method
        self.clip_range = clip_range
        self.params: Dict[str, np.ndarray] = {}
        self.is_fitted: bool = False

    def fit(self, X: Union[np.ndarray, List[List[float]]]) -> "FeatureScaler":
        """
        Computes the scaling parameters on clean training data.
        """
        arr = np.asarray(X, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)

        # Replace NaNs or Infs with column medians
        col_medians = np.nanmedian(arr, axis=0)
        inds = np.where(np.isnan(arr))
        arr[inds] = np.take(col_medians, inds[1])

        if self.method == "minmax":
            min_val = np.min(arr, axis=0)
            max_val = np.max(arr, axis=0)
            range_val = np.where((max_val - min_val) == 0, 1.0, max_val - min_val)
            self.params = {"min": min_val, "range": range_val}

        elif self.method == "standard":
            mean_val = np.mean(arr, axis=0)
            std_val = np.std(arr, axis=0)
            std_val = np.where(std_val == 0, 1.0, std_val)
            self.params = {"mean": mean_val, "std": std_val}

        elif self.method == "robust":
            median_val = np.median(arr, axis=0)
            q75, q25 = np.percentile(arr, [75, 25], axis=0)
            iqr = np.where((q75 - q25) == 0, 1.0, q75 - q25)
            self.params = {"median": median_val, "iqr": iqr}

        self.is_fitted = True
        return self

    def transform(self, X: Union[np.ndarray, List[List[float]]]) -> np.ndarray:
        """
        Applies fitted scaling parameters to new feature arrays.
        """
        if not self.is_fitted:
            raise RuntimeError("FeatureScaler has not been fitted yet. Call .fit(X) first.")

        arr = np.asarray(X, dtype=np.float32).copy()
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)

        # Clean NaNs
        for col_idx in range(arr.shape[1]):
            col = arr[:, col_idx]
            nan_mask = np.isnan(col) | np.isinf(col)
            if np.any(nan_mask):
                fill_val = (
                    self.params.get("min", [0.0])[col_idx]
                    if self.method == "minmax"
                    else 0.0
                )
                arr[nan_mask, col_idx] = fill_val

        if self.method == "minmax":
            scaled = (arr - self.params["min"]) / self.params["range"]
        elif self.method == "standard":
            scaled = (arr - self.params["mean"]) / self.params["std"]
        elif self.method == "robust":
            scaled = (arr - self.params["median"]) / self.params["iqr"]

        if self.clip_range is not None:
            scaled = np.clip(scaled, self.clip_range[0], self.clip_range[1])

        return scaled

    def fit_transform(self, X: Union[np.ndarray, List[List[float]]]) -> np.ndarray:
        """Convenience method to fit and transform in a single call."""
        return self.fit(X).transform(X)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes scaler parameters for storage."""
        return {
            "method": self.method,
            "clip_range": self.clip_range,
            "params": {k: v.tolist() for k, v in self.params.items()},
            "is_fitted": self.is_fitted,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeatureScaler":
        """Reconstructs scaler from dictionary."""
        scaler = cls(method=data["method"], clip_range=tuple(data["clip_range"]) if data["clip_range"] else None)
        scaler.params = {k: np.array(v, dtype=np.float32) for k, v in data["params"].items()}
        scaler.is_fitted = data["is_fitted"]
        return scaler
