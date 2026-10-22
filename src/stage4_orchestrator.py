"""
Stage 4: Central Pipeline Orchestrator & Consensus Engine
Runs Stage 1, Stage 2, and Stage 3 models simultaneously.
Coordinates data flow, routes cross-model GRAY lists, and executes the
Consensus Rules:
  - Any direct RED from Stage 1 or Stage 2 -> RED list.
  - If a player is marked GRAY across ALL 3 models -> Promote to RED list.
  - If a player is marked GRAY in only 1 or 2 models -> Keep in GRAY list.
  - Otherwise -> GREEN list.
Outputs the final rosters (GREEN / GRAY / RED) for developer enforcement handover.
"""

from typing import Dict, List, Any, Optional
from collections import defaultdict
try:
    from .stage1_passive_nlp import PassiveNLPDetector
    from .stage2_active_anomaly import ActiveAnomalyDetector
    from .stage3_agentic_profile import AgenticProfileInspector
except (ImportError, ValueError):
    from stage1_passive_nlp import PassiveNLPDetector
    from stage2_active_anomaly import ActiveAnomalyDetector
    from stage3_agentic_profile import AgenticProfileInspector


class PipelineOrchestrator:
    def __init__(
        self,
        stage1_detector: Optional[PassiveNLPDetector] = None,
        stage2_detector: Optional[ActiveAnomalyDetector] = None,
        stage3_inspector: Optional[AgenticProfileInspector] = None,
    ):
        self.stage1 = stage1_detector or PassiveNLPDetector()
        self.stage2 = stage2_detector or ActiveAnomalyDetector()
        self.stage3 = stage3_inspector or AgenticProfileInspector()

    def process_match_ecosystem(
        self,
        player_db_records: List[Dict[str, Any]],
        telemetry_stream: List[Dict[str, Any]],
        profile_records: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Executes the complete 4-stage pipeline across all connected data sources:
          1. Evaluates historical DB features via Stage 1 (NLP).
          2. Evaluates active in-game conditions via Stage 2 (Anomaly).
          3. Evaluates player profiles via Stage 3 (Agentic LLM).
          4. Merges, cross-evaluates, and resolves consensus tiers.
        """
        # Step 1: Execute Stage 1 (Passive NLP)
        s1_results = self.stage1.evaluate_batch(player_db_records)
        s1_green = set(s1_results["GREEN"])
        s1_gray = set(s1_results["GRAY"])
        s1_red = set(s1_results["RED"])

        # Step 2: Execute Stage 2 (Active Anomaly)
        s2_results = self.stage2.process_telemetry_batch(telemetry_stream)
        s2_gray = set(s2_results["GRAY"])
        s2_red = set(s2_results["RED"])

        # Step 3: Execute Stage 3 (Agentic Profile Inspector)
        s3_results = self.stage3.inspect_batch(profile_records)
        s3_green = set(s3_results["GREEN"])
        s3_gray = set(s3_results["GRAY"])

        # Step 4: Consensus Harmonization
        all_players = set()
        for r in player_db_records:
            all_players.add(r["player_id"])
        for t in telemetry_stream:
            all_players.add(t["player_id"])
        for p in profile_records:
            all_players.add(p["player_id"])

        final_roster = {"GREEN": [], "GRAY": [], "RED": []}
        player_audit_trail = {}

        for pid in sorted(all_players):
            is_s1_red = pid in s1_red
            is_s2_red = pid in s2_red
            
            is_s1_gray = pid in s1_gray
            is_s2_gray = pid in s2_gray
            is_s3_gray = pid in s3_gray

            gray_count = sum([1 if is_s1_gray else 0, 1 if is_s2_gray else 0, 1 if is_s3_gray else 0])

            # Consensus Logic:
            # 1. Direct RED from Stage 1 or Stage 2
            if is_s1_red or is_s2_red:
                final_tier = "RED"
                reason = "DIRECT_RED_FLAG (Critical violation in Stage 1 DB or Stage 2 Telemetry)"
            
            # 2. 3-GRAY Promotion Rule
            elif gray_count == 3:
                final_tier = "RED"
                reason = "3_GRAY_PROMOTION (Flagged as GRAY across Stage 1 NLP, Stage 2 Anomaly, and Stage 3 Profile Agent)"

            # 3. 2-GRAY or 1-GRAY Retention Rule
            elif gray_count in (1, 2):
                final_tier = "GRAY"
                reason = f"{gray_count}_GRAY_RETENTION (Flagged in {gray_count} of 3 models; retain in monitor queue)"

            # 4. Otherwise nominal
            else:
                final_tier = "GREEN"
                reason = "ALL_MODELS_NOMINAL (Clean baseline)"

            final_roster[final_tier].append(pid)
            player_audit_trail[pid] = {
                "final_tier": final_tier,
                "reason": reason,
                "stage1_status": "RED" if is_s1_red else ("GRAY" if is_s1_gray else "GREEN"),
                "stage2_status": "RED" if is_s2_red else ("GRAY" if is_s2_gray else "GREEN"),
                "stage3_status": "GRAY" if is_s3_gray else "GREEN",
                "gray_overlap_count": gray_count,
            }

        return {
            "summary": {
                "total_players": len(all_players),
                "green_count": len(final_roster["GREEN"]),
                "gray_count": len(final_roster["GRAY"]),
                "red_count": len(final_roster["RED"]),
            },
            "rosters": final_roster,
            "audit_trail": player_audit_trail,
            "developer_actions": {
                "GREEN": "Free / Allow normal play. Telemetry archived.",
                "GRAY": "Monitor / Increase tickrate to 128Hz, record full demo, queue for review.",
                "RED": "Ban or Quarantine / Immediate disconnect, HWID ban, or route to shadow-lobbies.",
            }
        }
