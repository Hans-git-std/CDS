"""
CDS (Cheat Detection System) - Developer Quickstart & Integration Tutorial
===========================================================================
This tutorial guides game developers through implementing the 4-Stage CDS framework:
  - Stage 1: Passive NLP Detector (Historical database stats, 5-layer TensorFlow Sequential)
  - Stage 2: Active Anomaly Detector (Live match telemetry, TensorFlow Deep Autoencoder)
  - Stage 3: Agentic Profile Inspector (Database seller intelligence, GREEN/GRAY invariant)
  - Stage 4: Central Pipeline Orchestrator (Multi-model consensus, 3-GRAY promotion, callbacks)
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

    # =========================================================================
    # STEP 1: STAGE 1 (PASSIVE NLP DETECTOR - HISTORICAL GAME DATABASE)
    # =========================================================================
    # Features chosen by developer: e.g. [Win Rate, KD Ratio, Headshot %, DPM]
    # CDS is feature-agnostic: choose whichever columns/stats exist in your game database!
    print("\n[Step 1] Initializing Stage 1 Passive NLP Detector (TensorFlow Sequential)...")
    stage1 = PassiveNLPDetector(auto_scale=True)

    # Ground truth Answer Key for first-time training:
    # Supply verified clean players (0) and confirmed banned cheaters (1).
    # NOTE: There is NO intermediate GRAY in training ground truth!
    clean_history = [
        [0.05, 0.08, 0.12, 0.15],
        [0.08, 0.10, 0.15, 0.18],
        [0.02, 0.05, 0.08, 0.10],
        [0.06, 0.09, 0.14, 0.16],
        [0.04, 0.07, 0.11, 0.13],
    ]
    banned_history = [
        [0.92, 0.95, 0.90, 0.88],
        [0.85, 0.88, 0.95, 0.91],
        [0.89, 0.90, 0.88, 0.85],
        [0.95, 0.98, 0.92, 0.90],
    ]

    # Combine into training arrays
    X_db_train = np.array(clean_history + banned_history, dtype=np.float32)
    y_db_train = np.array([0] * len(clean_history) + [1] * len(banned_history), dtype=np.float32)

    print("  -> Training Stage 1 with developer's Ground Truth Answer Key...")
    stage1.train(X_db_train, y_db_train, epochs=35, verbose=0)
    print("  -> Stage 1 Model trained & calibrated successfully!")

    # =========================================================================
    # STEP 2: STAGE 2 (ACTIVE ANOMALY DETECTOR - REAL-TIME LIVE TELEMETRY)
    # =========================================================================
    # Features chosen by developer: e.g. [Speed, Height, Combat Burst, Aim Delta]
    # Select whichever real-time telemetry variables your game server generates.
    print("\n[Step 2] Initializing Stage 2 Active Anomaly Detector (TensorFlow Autoencoder)...")
    stage2 = ActiveAnomalyDetector(auto_scale=True)

    # Train the Autoencoder on normal player movement ticks so it learns clean human physics.
    X_clean_telemetry = np.array([
        [0.25, 0.10, 0.20, 0.15],
        [0.30, 0.12, 0.25, 0.18],
        [0.22, 0.08, 0.18, 0.12],
        [0.28, 0.14, 0.22, 0.16],
        [0.35, 0.15, 0.30, 0.20],
        [0.24, 0.09, 0.19, 0.14],
        [0.29, 0.13, 0.23, 0.17],
        [0.26, 0.11, 0.21, 0.15],
    ], dtype=np.float32)

    print("  -> Training Stage 2 Autoencoder on clean gameplay baseline...")
    stage2.train_baseline(X_clean_telemetry, epochs=30, verbose=0)
    print("  -> Stage 2 Autoencoder calibrated! Thresholds adaptively derived.")

    # =========================================================================
    # STEP 3: STAGE 3 (AGENTIC PROFILE INSPECTOR - SELLER PATTERNS)
    # =========================================================================
    print("\n[Step 3] Initializing Stage 3 Agentic Profile Inspector...")
    stage3 = AgenticProfileInspector()
    print("  -> Ready to inspect profile text for cheat seller contact handles.")

    # =========================================================================
    # STEP 4: STAGE 4 (CENTRAL PIPELINE ORCHESTRATOR - SIMULTANEOUS RUN & CONSENSUS)
    # =========================================================================
    print("\n[Step 4] Running Stage 4 Orchestrator on Active Match Players...")

    # Attach studio moderation callbacks
    def on_player_banned(player_id, audit_info):
        print(f"  [STUDIO ENFORCEMENT ACTION] Banning {player_id}: {audit_info['reason']}")

    def on_player_monitored(player_id, audit_info):
        print(f"  [STUDIO ENFORCEMENT ACTION] Monitoring {player_id}: Sampling increased to 128Hz.")

    orchestrator = PipelineOrchestrator(
        stage1_detector=stage1,
        stage2_detector=stage2,
        stage3_inspector=stage3,
        on_gray_action=on_player_monitored,
        on_red_action=on_player_banned,
    )

    player_ids = [
        "Player_A_Clean",
        "Player_B_Borderline",
        "Player_C_StealthSeller",
        "Player_D_Speedhacker",
    ]

    # Historical DB stats queried from game database
    X_live_db = np.array([
        [0.05, 0.08, 0.12, 0.15],  # Player A: Very clean baseline -> GREEN (<0.35)
        [0.06, 0.09, 0.14, 0.16],  # Player B: Clean history -> GREEN (<0.35)
        [0.65, 0.68, 0.62, 0.60],  # Player C: Suspicious history -> GRAY [0.35 - 0.75]
        [0.92, 0.95, 0.90, 0.88],  # Player D: Blatant history -> RED (>=0.75)
    ], dtype=np.float32)

    # Live telemetry streamed from active match server
    X_live_telem = np.array([
        [0.26, 0.11, 0.21, 0.15],  # Player A: Normal -> Clean (Discarded early)
        [0.38, 0.18, 0.28, 0.22],  # Player B: Moderately anomalous -> GRAY
        [0.38, 0.18, 0.28, 0.22],  # Player C: Moderately anomalous -> GRAY
        [4.80, 5.50, 6.00, 5.90],  # Player D: Extreme speed/fly hack -> RED!
    ], dtype=np.float32)

    # User profile metadata extracted from game DB
    profiles = [
        {"player_id": "Player_A_Clean", "bio": "GG everyone, let's win!", "nickname": "Falcon"},
        {"player_id": "Player_B_Borderline", "bio": "Join our team clan discord.gg/teamalpha", "nickname": "AlphaOne"},
        {"player_id": "Player_C_StealthSeller", "bio": "Undetected VIP hacks available. DM on t.me/fast_cheats", "nickname": "Shadow"},
        {"player_id": "Player_D_Speedhacker", "bio": "Just having fun.", "nickname": "Flash99"},
    ]

    # 1. Run Stage 1 Passive Classification
    s1_res = stage1.classify(X_live_db, player_ids)
    # 2. Run Stage 2 Active Anomaly Detection (Discards GREEN immediately)
    s2_res = stage2.evaluate_telemetry(X_live_telem, player_ids)
    # 3. Run Stage 3 Agentic Profile Inspector (Outputs GREEN/GRAY only)
    s3_res = stage3.inspect_profiles(profiles)

    # 4. Harmonize via Stage 4 Pipeline Orchestrator
    consensus = orchestrator.harmonize_rosters(
        all_player_ids=player_ids,
        stage1_rosters=s1_res["rosters"],
        stage2_rosters=s2_res["rosters"],
        stage3_rosters=s3_res["rosters"],
        match_id="MATCH_BATTLEGROUND_ALPHA_99",
    )

    # =========================================================================
    # RESULTS & DEVELOPER HANDOVER
    # =========================================================================
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
        print(f"  Gray Overlap Count      : {audit['gray_overlap_count']}")
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
