"""
CDS (Cheat Detection System) - Newbie Developer Quickstart & Tutorial
======================================================================
This tutorial demonstrates how easily any game developer can integrate CDS:
  1. Define your own custom game features (CDS is completely feature-agnostic!).
  2. Train Stage 1 Passive Detector using your ground-truth Answer Key (0=GREEN, 1=RED).
  3. Train Stage 2 Active Detector (TensorFlow Autoencoder) on normal telemetry.
  4. Inspect player profiles via Stage 3 Agentic Profile Inspector.
  5. Run Stage 4 Pipeline Orchestrator with the 3-GRAY to RED consensus rule.
"""

import sys
import os
import numpy as np

# Add parent directory to path so cds package is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from cds import (
    PassiveNLPDetector,
    ActiveAnomalyDetector,
    AgenticProfileInspector,
    PipelineOrchestrator,
)


def main():
    print("=" * 80)
    print("  CDS (CHEAT DETECTION SYSTEM) - DEVELOPER INTEGRATION TUTORIAL")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # STEP 1: STAGE 1 (PASSIVE NLP DETECTOR - HISTORICAL GAME DATABASE)
    # -------------------------------------------------------------------------
    # NOTE: Features are decided by YOU (the developer), not by CDS!
    # Example Battleground features you might select:
    #   [win_rate_scaled, kd_ratio_scaled, headshot_rate_scaled, dpm_scaled]
    print("\n[Step 1] Initializing Stage 1 Passive NLP Detector (TensorFlow Sequential)...")
    stage1 = PassiveNLPDetector()

    # Ground-Truth Training Mode:
    # Provide your Answer Key: 0 for GREEN (clean players), 1 for RED (banned cheaters).
    # NOTE: In ground truth, there is NO mid-tier GRAY!
    clean_samples = [
        [0.02, 0.04, 0.08, 0.10], [0.05, 0.08, 0.12, 0.15],
        [0.03, 0.06, 0.10, 0.12], [0.06, 0.09, 0.14, 0.16],
        [0.04, 0.07, 0.11, 0.13], [0.02, 0.05, 0.09, 0.11],
        [0.05, 0.08, 0.13, 0.15], [0.04, 0.06, 0.10, 0.12],
    ]
    banned_samples = [
        [0.92, 0.95, 0.90, 0.88], [0.85, 0.88, 0.95, 0.91],
        [0.89, 0.90, 0.88, 0.85], [0.95, 0.98, 0.92, 0.90],
        [0.91, 0.94, 0.89, 0.87], [0.88, 0.92, 0.94, 0.89],
    ]
    X_db_train = np.array(clean_samples + banned_samples, dtype=np.float32)
    y_db_train = np.array([0] * len(clean_samples) + [1] * len(banned_samples), dtype=np.float32)

    print("  -> Training Stage 1 with developer's Ground Truth Answer Key...")
    stage1.train(X_db_train, y_db_train, epochs=50, verbose=0)
    print("  -> Stage 1 Model trained successfully!")

    # -------------------------------------------------------------------------
    # STEP 2: STAGE 2 (ACTIVE ANOMALY DETECTOR - REAL-TIME TELEMETRY)
    # -------------------------------------------------------------------------
    # NOTE: Again, features are decided by YOU!
    # Example real-time telemetry features:
    #   [movement_speed, player_elevation_delta, damage_per_min, micro_aim_jerk]
    print("\n[Step 2] Initializing Stage 2 Active Anomaly Detector (TensorFlow Autoencoder)...")
    stage2 = ActiveAnomalyDetector()

    # Train Autoencoder on normal, legitimate gameplay telemetry
    X_telemetry_clean = np.array([
        [0.25, 0.10, 0.20, 0.15],
        [0.30, 0.12, 0.25, 0.18],
        [0.22, 0.08, 0.18, 0.12],
        [0.28, 0.14, 0.22, 0.16],
        [0.35, 0.15, 0.30, 0.20],
    ], dtype=np.float32)

    print("  -> Training Stage 2 Autoencoder on clean gameplay baseline...")
    stage2.train_baseline(X_telemetry_clean, epochs=20, verbose=0)
    print("  -> Stage 2 Autoencoder calibrated!")

    # -------------------------------------------------------------------------
    # STEP 3: STAGE 3 (AGENTIC PROFILE INSPECTOR - SELLER PATTERNS)
    # -------------------------------------------------------------------------
    print("\n[Step 3] Initializing Stage 3 Agentic Profile Inspector...")
    stage3 = AgenticProfileInspector()
    print("  -> Ready to inspect profile text for cheat seller contact handles.")

    # -------------------------------------------------------------------------
    # STEP 4: STAGE 4 (CENTRAL ORCHESTRATOR - SIMULTANEOUS RUN & CONSENSUS)
    # -------------------------------------------------------------------------
    print("\n[Step 4] Running Stage 4 Orchestrator on Active Match Players...")
    orchestrator = PipelineOrchestrator(stage1, stage2, stage3)

    # Let's test with 4 players:
    #   Player A: Clean regular player (All GREEN -> Final GREEN)
    #   Player B: Borderline player (GRAY in S2 + S3 -> 2-GRAY Retention in GRAY)
    #   Player C: Stealth cheater (GRAY in S1 + S2 + S3 -> 3-GRAY Promotion to RED!)
    #   Player D: Blatant speedhacker (RED in S2 -> Direct RED!)
    player_ids = [
        "Player_A_Clean",
        "Player_B_Borderline",
        "Player_C_StealthSeller",
        "Player_D_Speedhacker",
    ]

    # Historical DB features (Stage 1)
    # Notice: features are continuous values scaled by the developer
    X_live_db = np.array([
        [0.02, 0.04, 0.07, 0.09],  # Player A: Very clean baseline -> GREEN (<0.35)
        [0.10, 0.12, 0.14, 0.15],  # Player B: Clean stats -> GREEN
        [0.32, 0.36, 0.30, 0.30],  # Player C: Suspicious stats -> GRAY [0.35 - 0.75]
        [0.85, 0.90, 0.88, 0.86],  # Player D: Blatant stats -> RED (>=0.75)
    ], dtype=np.float32)

    # Live Match Telemetry (Stage 2)
    X_live_telem = np.array([
        [0.26, 0.11, 0.22, 0.16],  # Player A: Normal -> Clean (Discarded)
        [0.55, 0.40, 0.50, 0.45],  # Player B: Moderately anomalous -> GRAY
        [0.55, 0.40, 0.50, 0.45],  # Player C: Moderately anomalous -> GRAY
        [1.80, 2.50, 2.00, 1.90],  # Player D: Extreme speed/fly hack -> RED!
    ], dtype=np.float32)

    # Profiles (Stage 3)
    profiles = [
        {"player_id": "Player_A_Clean", "bio": "GG everyone, let's win!", "nickname": "Falcon"},
        {"player_id": "Player_B_Borderline", "bio": "Join our clan discord.gg/teamalpha", "nickname": "AlphaOne"},
        {"player_id": "Player_C_StealthSeller", "bio": "Undetected VIP hacks available. DM on t.me/fast_cheats", "nickname": "Shadow"},
        {"player_id": "Player_D_Speedhacker", "bio": "Just having fun.", "nickname": "Flash99"},
    ]

    # Evaluate each stage
    s1_res = stage1.classify(X_live_db, player_ids)
    s2_res = stage2.evaluate_telemetry(X_live_telem, player_ids)
    s3_res = stage3.inspect_profiles(profiles)

    # Harmonize via Stage 4 Orchestrator
    consensus = orchestrator.harmonize_rosters(
        all_player_ids=player_ids,
        stage1_rosters=s1_res["rosters"],
        stage2_rosters=s2_res["rosters"],
        stage3_rosters=s3_res["rosters"],
    )

    # -------------------------------------------------------------------------
    # RESULTS & DEVELOPER HANDOVER
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("  FINAL CONSENSUS ROSTERS (STAGE 4 OUTPUT)")
    print("=" * 80)
    print(f"GREEN (Free to play)    : {consensus['rosters']['GREEN']}")
    print(f"GRAY  (Monitor / Queue) : {consensus['rosters']['GRAY']}")
    print(f"RED   (Ban / Disconnect): {consensus['rosters']['RED']}")

    print("\n--- Detailed Player Audit Trail ---")
    for pid, audit in consensus["audit_trail"].items():
        print(f"\nPlayer: {pid}")
        print(f"  Stage 1 (Passive DB)    : {audit['stage1_status']}")
        print(f"  Stage 2 (Active Telemetry): {audit['stage2_status']}")
        print(f"  Stage 3 (Profile Agent) : {audit['stage3_status']}")
        print(f"  Gray Overlap Count      : {audit['gray_count']}")
        print(f"  FINAL ACTION TIER       : ===> [{audit['final_tier']}] <===")
        print(f"  Reason                  : {audit['reason']}")

    print("\n" + "=" * 80)
    print("  DEVELOPER HANDOVER RESPONSIBILITY")
    print("=" * 80)
    for tier, action in consensus["developer_handover"].items():
        print(f"  [{tier}]: {action}")
    print("=" * 80)


if __name__ == "__main__":
    main()
