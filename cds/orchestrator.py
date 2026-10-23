"""
Stage 4: Central Pipeline Orchestrator & Consensus Engine
---------------------------------------------------------
Runs Stage 1, Stage 2, and Stage 3 simultaneously and balances their workloads.
Routes the cross-model GRAY lists and executes the Consensus Rules:
  - Direct RED: Any direct RED from Stage 1 or Stage 2 -> RED list.
  - 3-GRAY Promotion Rule: Flagged as GRAY in ALL THREE models -> Promoted to RED!
  - 2-GRAY Retention Rule: Flagged as GRAY in only 1 or 2 models -> Kept in GRAY.
  - Clean Baseline: Otherwise -> GREEN.
Outputs the final classified rosters (GREEN / GRAY / RED) for developer handover:
  - GREEN: Developer frees the player (normal matchmaking).
  - GRAY: Developer monitors the player (high-tick sampling, demo logging).
  - RED: Developer bans / quarantines the player.
"""

from typing import List, Dict, Any, Optional
from .passive_nlp import PassiveNLPDetector
from .active_anomaly import ActiveAnomalyDetector
from .agentic_profile import AgenticProfileInspector


class PipelineOrchestrator:
    def __init__(
        self,
        stage1_detector: Optional[PassiveNLPDetector] = None,
        stage2_detector: Optional[ActiveAnomalyDetector] = None,
        stage3_inspector: Optional[AgenticProfileInspector] = None,
    ):
        """
        Initializes the Stage 4 Orchestrator.
        """
        self.stage1 = stage1_detector or PassiveNLPDetector()
        self.stage2 = stage2_detector or ActiveAnomalyDetector()
        self.stage3 = stage3_inspector or AgenticProfileInspector()

    def harmonize_rosters(
        self,
        all_player_ids: List[str],
        stage1_rosters: Dict[str, List[str]],
        stage2_rosters: Dict[str, List[str]],
        stage3_rosters: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """
        Cross-evaluates the outputs of all three models using the Consensus Rules:
          1. Direct RED from Stage 1 or Stage 2 -> RED
          2. Flagged as GRAY in ALL 3 models -> RED (3-Gray Promotion)
          3. Flagged as GRAY in 1 or 2 models -> GRAY (Retained in monitor queue)
          4. Otherwise -> GREEN
        """
        s1_red = set(stage1_rosters.get("RED", []))
        s1_gray = set(stage1_rosters.get("GRAY", []))

        s2_red = set(stage2_rosters.get("RED", []))
        s2_gray = set(stage2_rosters.get("GRAY", []))

        s3_gray = set(stage3_rosters.get("GRAY", []))

        final_rosters = {"GREEN": [], "GRAY": [], "RED": []}
        audit_trail = {}

        for pid in sorted(set(all_player_ids)):
            is_direct_red = (pid in s1_red) or (pid in s2_red)

            is_s1_g = pid in s1_gray
            is_s2_g = pid in s2_gray
            is_s3_g = pid in s3_gray
            gray_count = sum([1 if is_s1_g else 0, 1 if is_s2_g else 0, 1 if is_s3_g else 0])

            if is_direct_red:
                final_tier = "RED"
                reason = "DIRECT_RED (Critical threshold exceeded in Stage 1 DB or Stage 2 Telemetry)"
            elif gray_count == 3:
                final_tier = "RED"
                reason = "3_GRAY_PROMOTION (Flagged as GRAY across Stage 1 NLP, Stage 2 Anomaly, and Stage 3 Profile)"
            elif gray_count in (1, 2):
                final_tier = "GRAY"
                reason = f"{gray_count}_GRAY_RETENTION (Flagged in {gray_count} of 3 models; retain in monitor queue)"
            else:
                final_tier = "GREEN"
                reason = "ALL_MODELS_CLEAN (Nominal gameplay baseline)"

            final_rosters[final_tier].append(pid)
            audit_trail[pid] = {
                "final_tier": final_tier,
                "reason": reason,
                "stage1_status": "RED" if pid in s1_red else ("GRAY" if is_s1_g else "GREEN"),
                "stage2_status": "RED" if pid in s2_red else ("GRAY" if is_s2_g else "GREEN"),
                "stage3_status": "GRAY" if is_s3_g else "GREEN",
                "gray_count": gray_count,
            }

        return {
            "summary": {
                "total_players": len(all_player_ids),
                "green_count": len(final_rosters["GREEN"]),
                "gray_count": len(final_rosters["GRAY"]),
                "red_count": len(final_rosters["RED"]),
            },
            "rosters": final_rosters,
            "audit_trail": audit_trail,
            "developer_handover": {
                "GREEN": "Free / Allow normal play.",
                "GRAY": "Monitor / Increase tick sampling rate, record demo, soft trust queue.",
                "RED": "Ban or Quarantine / Disconnect, HWID ban, or route to shadow-lobbies.",
            }
        }
