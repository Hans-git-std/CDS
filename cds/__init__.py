"""
CDS (Cheat Detection System)
============================
Developer Framework for Multi-Modal Anti-Cheat Architecture.
"""

from .scaler import FeatureScaler
from .passive_nlp import PassiveNLPDetector
from .active_anomaly import ActiveAnomalyDetector
from .agentic_profile import AgenticProfileInspector
from .orchestrator import PipelineOrchestrator

__version__ = "2.2.0"
__all__ = [
    "FeatureScaler",
    "PassiveNLPDetector",
    "ActiveAnomalyDetector",
    "AgenticProfileInspector",
    "PipelineOrchestrator",
]
