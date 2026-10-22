"""
End-to-End Simulation Example of the CDS 4-Stage Architecture.
Demonstrates:
  1. Cold-start training mode with binary GREEN/RED answer key.
  2. Stage 1 Passive NLP on historical DB stats.
  3. Stage 2 Active Anomaly on live game telemetry.
  4. Stage 3 Agentic Profile Inspector on bio/contact text.
  5. Stage 4 Pipeline Orchestrator with the 3-GRAY -> RED promotion rule.
"""

from stage1_passive_nlp import PassiveNLPDetector
from stage2_active_anomaly import ActiveAnomalyDetector
from stage3_agentic_profile import AgenticProfileInspector
from stage4_orchestrator import PipelineOrchestrator


def main():
    print("=" * 80)
    print("  CDS (CHEAT DETECTION SYSTEM) - 4-STAGE BATTLEGROUND SIMULATION")
    print("=" * 80)

    # 1. Initialize Stage 1 Detector & Run First-Time Training
    stage1 = PassiveNLPDetector()
    ground_truth_answer_key = [
        {"player_id": "TRAIN_LEGIT_1", "stats": {"win_rate": 0.08, "kd_ratio": 1.1, "headshot_rate": 0.18, "damage_per_match": 280.0}, "label": "GREEN"},
        {"player_id": "TRAIN_LEGIT_2", "stats": {"win_rate": 0.15, "kd_ratio": 2.2, "headshot_rate": 0.28, "damage_per_match": 450.0}, "label": "GREEN"},
        {"player_id": "TRAIN_BANNED_1", "stats": {"win_rate": 0.88, "kd_ratio": 22.0, "headshot_rate": 0.91, "damage_per_match": 2200.0}, "label": "RED"},
    ]
    stage1.train(ground_truth_answer_key)

    stage2 = ActiveAnomalyDetector()
    stage3 = AgenticProfileInspector()
    orchestrator = PipelineOrchestrator(stage1, stage2, stage3)

    # Simulated Battleground Player Data
    # P101: Clean Veteran Player
    # P102: Stealth Cheater & Seller (GRAY in S1, GRAY in S2, GRAY in S3 -> Should be promoted to RED!)
    # P103: Skilled Smurf (GRAY in S1, GREEN in S2, GREEN in S3 -> Should stay GRAY)
    # P104: Blatant Speedhacker (RED in S2 -> Instant RED)

    db_records = [
        {"player_id": "P101_Clean_Player", "stats": {"win_rate": 0.12, "kd_ratio": 1.4, "headshot_rate": 0.20, "damage_per_match": 320.0}},
        {"player_id": "P102_Stealth_Seller", "stats": {"win_rate": 0.38, "kd_ratio": 4.8, "headshot_rate": 0.48, "damage_per_match": 980.0}},
        {"player_id": "P103_Skilled_Smurf", "stats": {"win_rate": 0.32, "kd_ratio": 4.2, "headshot_rate": 0.45, "damage_per_match": 850.0}},
        {"player_id": "P104_Blatant_Speed", "stats": {"win_rate": 0.25, "kd_ratio": 3.0, "headshot_rate": 0.30, "damage_per_match": 600.0}},
    ]

    telemetry_stream = [
        {"player_id": "P101_Clean_Player", "movement_speed": 12.0, "player_height": 10.0, "active_dpm": 400.0, "active_kd": 1.0, "active_headshot_rate": 0.20, "micro_aim_snap": False},
        {"player_id": "P102_Stealth_Seller", "movement_speed": 18.5, "player_height": 22.0, "active_dpm": 1600.0, "active_kd": 4.0, "active_headshot_rate": 0.60, "micro_aim_snap": True},
        {"player_id": "P103_Skilled_Smurf", "movement_speed": 13.0, "player_height": 12.0, "active_dpm": 700.0, "active_kd": 2.5, "active_headshot_rate": 0.35, "micro_aim_snap": False},
        {"player_id": "P104_Blatant_Speed", "movement_speed": 45.0, "player_height": 15.0, "active_dpm": 2900.0, "active_kd": 8.0, "active_headshot_rate": 0.85, "micro_aim_snap": True},
    ]

    profile_records = [
        {"player_id": "P101_Clean_Player", "nickname": "ViperStrike", "bio": "Just chilling with squad.", "clan_tag": "[DELTA]"},
        {"player_id": "P102_Stealth_Seller", "nickname": "Ez_Frags_99", "bio": "Undetected VIP config available. Add t.me/ez_win_cheats or DC: seller#123", "clan_tag": "[VIP]"},
        {"player_id": "P103_Skilled_Smurf", "nickname": "AlternateSmurf", "bio": "Road to top 500.", "clan_tag": "[SOLO]"},
        {"player_id": "P104_Blatant_Speed", "nickname": "SonicSpeed", "bio": "Gotta go fast.", "clan_tag": "[RACE]"},
    ]

    print("\n[Stage 4 Orchestrator] Running all models simultaneously...")
    results = orchestrator.process_match_ecosystem(db_records, telemetry_stream, profile_records)

    print("\n" + "=" * 80)
    print("  ORCHESTRATOR CONSENSUS RESULTS")
    print("=" * 80)
    print(f"Total Players Processed: {results['summary']['total_players']}")
    print(f"  • GREEN (Clean / Free)     : {results['rosters']['GREEN']}")
    print(f"  • GRAY  (Monitor / Queue)  : {results['rosters']['GRAY']}")
    print(f"  • RED   (Ban / Quarantine) : {results['rosters']['RED']}")

    print("\n--- Detailed Audit Trail ---")
    for pid, audit in results["audit_trail"].items():
        print(f"\nPlayer: {pid}")
        print(f"  Stage 1 (Passive NLP):    {audit['stage1_status']}")
        print(f"  Stage 2 (Active Anomaly): {audit['stage2_status']}")
        print(f"  Stage 3 (Profile Agent):  {audit['stage3_status']}")
        print(f"  Gray Overlap Count:       {audit['gray_overlap_count']}")
        print(f"  FINAL VERDICT:            --> [{audit['final_tier']}] <--")
        print(f"  Reason:                   {audit['reason']}")

    print("\n" + "=" * 80)
    print("  DEVELOPER ACTION HANDOVER")
    print("=" * 80)
    for tier, action in results["developer_actions"].items():
        print(f"[{tier}] Action for Developer: {action}")
    print("=" * 80)


if __name__ == "__main__":
    main()
