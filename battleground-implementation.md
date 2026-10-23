# 🎮 Developer Guide: Integrating CDS into Your Game (`battleground-implementation.md`)

Welcome to the **CDS (Cheat Detection System) Developer Implementation Guide**.  
This tutorial is designed so that **any developer—even a beginner—can easily implement multi-stage cheat detection** into their game (such as modern multiplayer Battlegrounds, Battle Royale titles, or competitive shooters).

---

## 📌 Core Rule: Features are Decided by YOU

> [!IMPORTANT]
> **CDS is completely feature-agnostic.**  
> We do **not** force or hardcode specific features into the models. As the game developer, **you decide which features to extract from your game database and live match servers**.  
> CDS automatically adapts to whatever number of features (`input_dim`) you provide.

---

## 🧠 What Types of Features Should You Use? (Guidance & Ideas)

To help you get started, here is a guide on the types of features you can select for your game:

### 1. Historical Database Features (For Stage 1: Passive NLP Detector)
Extract cumulative historical stats per player from your user database:
* **Win Ratios:** e.g., `wins / total_matches` (Normal: 5%–15%, Cheater: 70%–95%)
* **Kill-to-Death Ratios (K/D):** (Normal: 1.0–3.0, Cheaters: 15.0–40.0)
* **Headshot Ratios:** `headshot_kills / total_kills` (Normal: 15%–30%, Aimbot: 80%–98%)
* **Damage Output:** Average damage per match
* **Account Lifetime:** Matches played or account age in days (detects burner accounts)

> **💡 Best Practice:** Always scale/normalize your features to approximately $[0.0, 1.0]$ before passing them to the model (e.g. `kd_ratio / 20.0`).

### 2. Live Match Telemetry Features (For Stage 2: Active Anomaly Detector)
Stream high-frequency live match updates from your game server:
* **Movement Velocity:** Instantaneous player speed (detects speed-hacks)
* **Player Elevation / Height:** Vertical coordinate deltas (detects fly-hacks or super-jumps)
* **Active Match DPM:** Real-time damage per minute during the ongoing match
* **Aim Kinematics:** Angular rotation speed, snap deltas, or reticle jerks
* **Reaction Times:** Millisecond delay between enemy visibility and first shot

---

## 🚀 Step-by-Step Implementation

### Step 1: Install Dependencies
CDS relies on **TensorFlow** and **NumPy**:

```bash
pip install tensorflow numpy
```

---

### Step 2: Stage 1 — Passive Detector (TensorFlow Sequential)

Stage 1 runs a **TensorFlow Sequential Neural Network** against your historical game database.

#### The Cold-Start Training Mode (First-Time Setup):
When initializing CDS for your game for the first time, you run in **Training Mode**:
* Provide an **Answer Key** of known **GREEN** (verified legitimate players, labeled `0`) and **RED** (previously banned cheaters, labeled `1`).
* **Why no GRAY in training?** In ground truth, there is no mid-tier GRAY—a player is either clean or a cheater. The neural network learns the boundary between clean and banned behavior, and will automatically infer suspicious intermediate **GRAY** players during live inference.

#### Python Code:
```python
from cds import PassiveNLPDetector
import numpy as np

# 1. Initialize detector
stage1 = PassiveNLPDetector()

# 2. Prepare your ground truth training data (Features chosen by YOU!)
# In this example, the developer chose 4 features: [win_rate, kd, headshot_rate, dpm]
X_train = np.array([
    # Clean players (0 = GREEN)
    [0.05, 0.08, 0.12, 0.15],
    [0.08, 0.10, 0.15, 0.18],
    [0.02, 0.05, 0.08, 0.10],
    # Confirmed cheaters (1 = RED)
    [0.92, 0.95, 0.90, 0.88],
    [0.85, 0.88, 0.95, 0.91],
    [0.89, 0.90, 0.88, 0.85],
], dtype=np.float32)

y_train = np.array([0, 0, 0, 1, 1, 1], dtype=np.float32)

# 3. Train model with your answer key
stage1.train(X_train, y_train, epochs=30)

# 4. Run live classification on players from your DB
live_players_data = np.array([
    [0.04, 0.06, 0.10, 0.12], # Clean player
    [0.25, 0.28, 0.22, 0.20], # Borderline suspicious
], dtype=np.float32)

results = stage1.classify(live_players_data, player_ids=["Player_101", "Player_102"])
# Returns:
# results["rosters"]["GREEN"] -> List of clean player IDs
# results["rosters"]["GRAY"]  -> List of suspicious player IDs
# results["rosters"]["RED"]   -> List of confirmed cheater IDs
```

---

### Step 3: Stage 2 — Active Detector (TensorFlow Autoencoder)

Stage 2 runs concurrently and independently during live matches to inspect in-game telemetry:
* Uses a **TensorFlow Sequential Deep Autoencoder** to learn normal human gameplay.
* **Auto-filtering Optimization:** Clean players (**GREEN**) have low reconstruction error and are **automatically removed/discarded immediately** to save server CPU.
* Only **GRAY** (suspicious deviations) and **RED** (critical kinematic exploits) are reported.

#### Python Code:
```python
from cds import ActiveAnomalyDetector
import numpy as np

stage2 = ActiveAnomalyDetector()

# 1. Calibrate on legitimate clean gameplay telemetry
# Features chosen by YOU (e.g. [speed, elevation, combat_burst, aim_snap])
X_clean_telemetry = np.array([
    [0.25, 0.10, 0.20, 0.15],
    [0.30, 0.12, 0.25, 0.18],
    [0.22, 0.08, 0.18, 0.12],
], dtype=np.float32)

stage2.train_baseline(X_clean_telemetry, epochs=25)

# 2. Evaluate active players in live match
X_live_telemetry = np.array([
    [0.26, 0.11, 0.22, 0.16], # Normal player -> Discarded (GREEN)
    [0.55, 0.40, 0.50, 0.45], # Moderate anomaly -> GRAY
    [1.80, 2.50, 2.00, 1.90], # Extreme speed/fly hack -> RED
], dtype=np.float32)

live_results = stage2.evaluate_telemetry(X_live_telemetry, player_ids=["P1", "P2", "P3"])
# live_results["rosters"]["GRAY"] -> ["P2"]
# live_results["rosters"]["RED"]  -> ["P3"]
# P1 was automatically discarded to conserve memory!
```

---

### Step 4: Stage 3 — Agentic Profile Inspector (Seller Intelligence)

Many aggressive cheaters monetize their hacks by putting their contact information (Discord, Telegram, WhatsApp, "DM for cheat") in their profile bio, username, or clan tag.

* Stage 3 pulls profile metadata from your database and scans for seller patterns.
* **Safety Rule:** A profile alone **cannot definitively brand a player RED**. Therefore, Stage 3 outputs **ONLY GREEN and GRAY**.

#### Python Code:
```python
from cds import AgenticProfileInspector

stage3 = AgenticProfileInspector()

profiles = [
    {"player_id": "P1", "nickname": "Shadow", "clan_tag": "[VIP]", "bio": "Join t.me/fast_cheats for undetected aimbot"},
    {"player_id": "P2", "nickname": "Viper", "clan_tag": "[TEAM]", "bio": "Having fun with friends"},
]

profile_results = stage3.inspect_profiles(profiles)
# P1 -> GRAY (Commercial seller tags detected)
# P2 -> GREEN (Clean profile)
```

---

### Step 5: Stage 4 — Pipeline Orchestrator & Consensus Engine

Stage 4 runs all models simultaneously and balances their work. Its primary role is to **cross-evaluate the GRAY lists** across models:

#### The Consensus Rules:
1. **Direct RED Rule:** If Stage 1 or Stage 2 outputs `RED` $\rightarrow$ final verdict is **RED**.
2. **The 3-GRAY Promotion Rule:** If a player is marked as `GRAY` across **ALL THREE models** (Stage 1 Passive, Stage 2 Active, AND Stage 3 Profile) $\rightarrow$ **Promote to RED**!
3. **The 2-GRAY Retention Rule:** If marked as `GRAY` in only 1 or 2 models $\rightarrow$ **Keep in GRAY** (retain in monitor queue).
4. **Clean Rule:** Otherwise $\rightarrow$ **GREEN**.

#### Python Code:
```python
from cds import PipelineOrchestrator

orchestrator = PipelineOrchestrator(stage1, stage2, stage3)

# Pass all outputs into the Orchestrator
final_verdict = orchestrator.harmonize_rosters(
    all_player_ids=["P1", "P2", "P3"],
    stage1_rosters=results["rosters"],
    stage2_rosters=live_results["rosters"],
    stage3_rosters=profile_results["rosters"],
)

print("GREEN (Clean)    :", final_verdict["rosters"]["GREEN"])
print("GRAY  (Monitor)  :", final_verdict["rosters"]["GRAY"])
print("RED   (Cheater)  :", final_verdict["rosters"]["RED"])
```

---

## 🛡️ Developer Handover & Action Guide

Once CDS returns the final classified rosters, **you (the game developer) take action according to your studio policies**. CDS carries no moderation liability:

| Tier | Recommended Developer Action |
| :--- | :--- |
| **`GREEN`** | **Free / Normal Play:** Player continues standard matchmaking. |
| **`GRAY`** | **Monitor:** Increase server tickrate sampling (e.g. to 128Hz), record match replay demo, or place in soft trust-factor queue. |
| **`RED`** | **Ban / Disconnect:** Immediate disconnect, HWID/account ban, or silent quarantine into shadow-lobbies (cheaters vs cheaters). |
