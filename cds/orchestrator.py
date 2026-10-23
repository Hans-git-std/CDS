"""
Stage 4: Central Pipeline Orchestrator & Consensus Engine
=========================================================
Coordinates Stage 1, Stage 2, and Stage 3 models simultaneously and balances their work.
Routes cross-model GRAY lists and executes the Consensus Rules:

Consensus Rules:
  1. Direct RED: Any direct RED from Stage 1 DB or Stage 2 Telemetry -> RED list.
  2. The 3-GRAY Promotion Rule: Flagged as GRAY across ALL THREE models -> Promoted to RED!
  3. The 2-GRAY Retention Rule: Flagged as GRAY in only 1 or 2 models -> Kept in GRAY (monitor queue).
  4. Nominal Baseline: Otherwise -> GREEN list.

Developer Handover Responsibility:
  - GREEN: Free the player (normal matchmaking).
  - GRAY: Monitor the player (128Hz telemetry recording, full demo replay, soft trust queue).
  - RED: Ban or quarantine the player (match disconnect, HWID/account ban, shadow-lobbies).
"""

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timezone
import logging

from .passive_nlp import PassiveNLPDetector
from .active_anomaly import ActiveAnomalyDetector
from .agentic_profile import AgenticProfileInspector

logger = logging.getLogger("cds.orchestrator")


class PipelineOrchestrator:
    """
    Central consensus engine coordinating multi-modal anti-cheat detection stages.
    """

    def __init__(
        self,
        stage1_detector: Optional[PassiveNLPDetector] = None,
        stage2_detector: Optional[ActiveAnomalyDetector] = None,
        stage3_inspector: Optional[AgenticProfileInspector] = None,
        on_green_action: Optional[Callable[[str], None]] = None,
        on_gray_action: Optional[Callable[[str, Dict[str, Any]], None]] = None,
        on_red_action: Optional[Callable[[str, Dict[str, Any]], None]] = None,
    ):
        """
        :param stage1_detector: Configured Stage 1 Passive NLP Detector.
        :param stage2_detector: Configured Stage 2 Active Anomaly Detector.
        :param stage3_inspector: Configured Stage 3 Agentic Profile Inspector.
        :param on_green_action: Optional developer callback for GREEN players.
        :param on_gray_action: Optional developer callback for GRAY players.
        :param on_red_action: Optional developer callback for RED players.
        """
        self.stage1 = stage1_detector or PassiveNLPDetector()
        self.stage2 = stage2_detector or ActiveAnomalyDetector()
        self.stage3 = stage3_inspector or AgenticProfileInspector()

        self.on_green_action = on_green_action
        self.on_gray_action = on_gray_action
        self.on_red_action = on_red_action

    def harmonize_rosters(
        self,
        all_player_ids: List[str],
        stage1_rosters: Dict[str, List[str]],
        stage2_rosters: Dict[str, List[str]],
        stage3_rosters: Dict[str, List[str]],
        match_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Consolidates outputs across Stage 1, Stage 2, and Stage 3 into final GREEN/GRAY/RED rosters.
        """
        s1_red = set(stage1_rosters.get("RED", []))
        s1_gray = set(stage1_rosters.get("GRAY", []))

        s2_red = set(stage2_rosters.get("RED", []))
        s2_gray = set(stage2_rosters.get("GRAY", []))

        s3_gray = set(stage3_rosters.get("GRAY", []))

        final_rosters: Dict[str, List[str]] = {"GREEN": [], "GRAY": [], "RED": []}
        audit_trail: Dict[str, Dict[str, Any]] = {}

        unique_players = sorted(set(all_player_ids))

        for pid in unique_players:
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

            audit_info = {
                "player_id": pid,
                "final_tier": final_tier,
                "reason": reason,
                "stage1_status": "RED" if pid in s1_red else ("GRAY" if is_s1_g else "GREEN"),
                "stage2_status": "RED" if pid in s2_red else ("GRAY" if is_s2_g else "GREEN"),
                "stage3_status": "GRAY" if is_s3_g else "GREEN",
                "gray_overlap_count": gray_count,
            }
            audit_trail[pid] = audit_info

            # Execute optional developer callbacks
            if final_tier == "GREEN" and self.on_green_action:
                self.on_green_action(pid)
            elif final_tier == "GRAY" and self.on_gray_action:
                self.on_gray_action(pid, audit_info)
            elif final_tier == "RED" and self.on_red_action:
                self.on_red_action(pid, audit_info)

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "match_id": match_id or "MATCH_UNSPECIFIED",
            "summary": {
                "total_players": len(unique_players),
                "green_count": len(final_rosters["GREEN"]),
                "gray_count": len(final_rosters["GRAY"]),
                "red_count": len(final_rosters["RED"]),
            },
            "rosters": final_rosters,
            "audit_trail": audit_trail,
            "developer_handover": {
                "GREEN": "Free / Allow normal play. Telemetry archived.",
                "GRAY": "Monitor / Increase tickrate to 128Hz, record full demo, queue for review.",
                "RED": "Ban or Quarantine / Immediate disconnect, HWID ban, or route to shadow-lobbies.",
            },
        }

        logger.info(
            "Consensus executed. Total: %d | GREEN: %d | GRAY: %d | RED: %d",
            len(unique_players),
            len(final_rosters["GREEN"]),
            len(final_rosters["GRAY"]),
            len(final_rosters["RED"]),
        )
        return payload
