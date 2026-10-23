# 🎮 Developer Guide: Integrating CDS into Your Game (`battleground-implementation.md`)

Welcome to the **CDS (Cheat Detection System) Developer Implementation Guide**.  
This tutorial is designed so that **any developer—even a newbie—can easily integrate multi-stage cheat detection** into their game (such as modern multiplayer Battlegrounds, Battle Royale titles, tactical shooters, or competitive arenas).

---

> [!NOTE]
> **Implementation Code Location:**  
> This file is the integration guide and tutorial. The actual core framework code is located in the **`cds/`** package:
> * [`cds/scaler.py`](cds/scaler.py) — Dynamic feature preprocessor (MinMax, Standard, Robust, serialization)
> * [`cds/passive_nlp.py`](cds/passive_nlp.py) — Stage 1 Passive 5-layer TensorFlow Sequential detector
> * [`cds/active_anomaly.py`](cds/active_anomaly.py) — Stage 2 Active deep autoencoder with early GREEN discard
> * [`cds/agentic_profile.py`](cds/agentic_profile.py) — Stage 3 Anti-obfuscation seller profile inspector
> * [`cds/orchestrator.py`](cds/orchestrator.py) — Stage 4 Consensus engine & studio action dispatcher
> * [`examples/quickstart_tutorial.py`](examples/quickstart_tutorial.py) — Runnable end-to-end integration tutorial

---

## 📌 Core Rule: Features are Decided by YOU

> [!IMPORTANT]
> **CDS is completely feature-agnostic.**  
> We do **not** force or hardcode specific database columns or telemetry metrics into our algorithms. As the game developer, **you decide which features to extract from your game database and live match servers**.  
> CDS automatically adapts to whatever number of features (`input_dim`) you provide.

---

## 🧠 Step 1: Feature Selection & Scaling (How to Build 64–128 Features)

To achieve high detection accuracy while avoiding false positives, we guide developers to construct an extensive feature vector of **64 to 128 features** from your game database.

### 1. Feature Ideas for Battleground Titles (Target: 64 to 128 Features)

You can assemble your feature vector by combining metrics across five core game categories:

| Category | Example Metrics to Extract from Game DB (Choose 12–25 per category) | Normal Range | Cheater Indicator |
| :--- | :--- | :--- | :--- |
| **⚔️ Combat Efficiency** | Win Rate, Overall K/D, Headshot-to-Kill %, Damage Per Match (DPM), Sniper Longshot Accuracy %, Assault Rifle burst headshot ratio, Time-to-Kill (TTK) percentiles, Grenade kill ratio. | Win: 5%–15%<br>K/D: 1.0–2.5<br>HS: 15%–25% | Win: > 70%<br>K/D: > 15.0<br>HS: > 80% |
| **🏃 Movement & Mobility** | Average sprint speed, Vertical elevation delta variance, Foot travel vs Vehicle travel ratio, Out-of-bounds trigger frequency, Safe-zone travel speed, Water swim speed. | Sprint: 5–7 m/s<br>Z-delta: Normal jumps | Speed: > 20 m/s<br>Fly: abnormal Z deltas |
| **🎯 Aim & Target Acquisition** | Angular rotation velocity, Reticle jerk standard deviation, Target snap reaction time (ms), Crosshair pre-placement on occluded enemies, Spray pattern consistency. | Reaction: 180–300ms<br>Spray: Variable jitter | Reaction: < 40ms<br>Spray: Zero variance |
| **🎒 Loot & Weapon Mastery** | Time to acquire Tier-3 armor/weapons, Airdrop crate loot latency, Kill count per weapon class, First-shot hit probability, Ammo expenditure efficiency. | Balanced across match duration | Instantly loots rare crates; 90%+ hit efficiency |
| **📅 Account & Social Signal** | Account lifetime (days), Total matches played, Match survival duration std-dev, Report-to-match ratio, Teammate revive frequency, Clan tag length. | Mature account (>60 days)<br>Reports: < 2% | Burner account (< 2 days)<br>Reports: > 40% |

---

### 2. The Feature Scaling Pipeline (Raw DB Data ➡️ Model Input)

Raw metrics have drastically different units: K/D is $0–30$, Account Age is $0–1000$ days, and Headshot Ratio is $0.0–1.0$. Passing unscaled data directly into neural networks causes gradient instability.

CDS provides a dedicated [`FeatureScaler`](cds/scaler.py) that handles this automatically:

```python
from cds import FeatureScaler
import numpy as np

# 1. Initialize scaler (method can be 'minmax', 'standard', or 'robust')
scaler = FeatureScaler(method="standard")

# 2. Extract raw 64 to 128 features from your player database
raw_db_features = np.array([
    [0.12, 1.85, 0.22, 450.0, 180.0],  # Verified clean player
    [0.88, 28.5, 0.94, 2850.0, 3.0],   # Banned burner account
], dtype=np.float32)

# 3. Fit and scale features into normalized distribution
scaled_features = scaler.fit_transform(raw_db_features)
print("Scaled input shape:", scaled_features.shape)
```

---

## 🚀 Step 2: First-Time Setup & Cold-Start Training Mode

When initializing CDS for your game for the first time, you run Stage 1 in **Cold-Start Training Mode**:

```
+-----------------------------------------------------------------------------------+
|                           STAGE 1 COLD-START TRAINING                             |
+-----------------------------------------------------------------------------------+
|  1. Verified Legitimate Players  (Historical DB)   --> Label = 0  (GREEN)         |
|  2. Confirmed Banned Cheaters    (Security DB)     --> Label = 1  (RED)           |
|                                                                                   |
|  * Note: In real life training ground truth, there is NO mid-tier GRAY.           |
|    A player is either verified clean (0) or confirmed banned (1).                 |
|    The 5-layer neural network automatically learns to infer suspicious GRAYs!     |
+-----------------------------------------------------------------------------------+
```

### Complete Cold-Start Python Code:

```python
from cds import PassiveNLPDetector, FeatureScaler
import numpy as np

# 1. Initialize detector (CDS automatically builds the 5-layer TensorFlow Sequential network)
#    Architecture:
#      - Layer 1: Dense(input_dim units, ReLU)  [Guidance: 64 to 128 features]
#      - Layer 2: Dense(input_dim // 2 units, ReLU)
#      - Layer 3: Dense(input_dim // 2 units, ReLU)
#      - Layer 4: Dense(input_dim // 4 units, ReLU)
#      - Layer 5: Dense(1 unit, Sigmoid) -> Binary risk probability [0.0 to 1.0]
stage1 = PassiveNLPDetector(
    gray_threshold_low=0.35,  # Scores < 0.35 are GREEN (Clean)
    gray_threshold_high=0.75, # Scores > 0.75 are RED (Banned)
    auto_scale=True           # Automatically applies FeatureScaler
)

# 2. Prepare your ground truth training data (Features chosen by YOU)
X_historical_db = np.array([
    # Verified Clean Players (Answer Key: 0 = GREEN)
    [0.08, 1.45, 0.18, 380.0, 240.0],
    [0.12, 2.10, 0.22, 450.0, 180.0],
    [0.05, 0.95, 0.14, 290.0, 310.0],
    # Confirmed Banned Cheaters (Answer Key: 1 = RED)
    [0.85, 24.5, 0.91, 2400.0, 2.0],
    [0.92, 38.0, 0.96, 3100.0, 1.0],
    [0.78, 19.8, 0.88, 1950.0, 4.0],
], dtype=np.float32)

# Ground truth Answer Key: 0=GREEN, 1=RED (NO GRAY IN GROUND TRUTH)
y_answer_key = np.array([0, 0, 0, 1, 1, 1], dtype=np.float32)

# 3. Train the model on your database answer key
stage1.train(X_historical_db, y_answer_key, epochs=35, batch_size=16)

# 4. Save your trained model & scaler for production inference
stage1.save("models/stage1_passive_nlp")
print("Stage 1 model and FeatureScaler saved successfully.")
```

---

## 🔍 Step 3: Stage 1 Live Inference (Rectified for Newbie Developers)

Once trained, here is how a developer passes live, unverified players from their game database to get tri-state classifications:

```python
from cds import PassiveNLPDetector
import numpy as np

# 1. Load trained Stage 1 detector
stage1 = PassiveNLPDetector.load("models/stage1_passive_nlp")

# 2. Query your game database for active players to inspect
live_players_data = np.array([
    [0.10, 1.60, 0.19, 410.0, 200.0], # Normal player
    [0.45, 6.80, 0.52, 980.0, 45.0],  # Borderline suspicious (high KD, low days)
    [0.95, 34.0, 0.95, 2900.0, 1.0],  # Blatant cheater burner account
], dtype=np.float32)

player_ids = ["Player_Alice", "Player_Bob", "Player_Charlie"]

# 3. Run classification
classification_result = stage1.classify(live_players_data, player_ids=player_ids)

# 4. Inspect classified rosters and take studio action:
green_list = classification_result["rosters"]["GREEN"] # Legitimate players -> Free to play
gray_list  = classification_result["rosters"]["GRAY"]  # Borderline -> Forward to Stage 4 & monitor
red_list   = classification_result["rosters"]["RED"]   # Cheater -> Flag for immediate ban

print("GREEN (Clean)    :", green_list) # e.g. ['Player_Alice']
print("GRAY  (Suspicious):", gray_list)  # e.g. ['Player_Bob']
print("RED   (Cheater)   :", red_list)   # e.g. ['Player_Charlie']

# Access exact continuous risk probabilities [0.0 to 1.0] for detailed audit:
for item in classification_result["predictions"]:
    print(f"Player {item['player_id']}: Risk={item['risk_score']:.3f} -> Category={item['category']}")
```

---

## ⚡ Step 4: Stage 2 — Active Anomaly Detector (Live Match Telemetry)

Stage 2 runs concurrently and independently during live battleground matches.  
It monitors real-time telemetry (movement speed, elevation delta, weapon firing bursts, reticle snaps):

* **TensorFlow Deep Autoencoder:** Learns the compression and reconstruction of legitimate human physical telemetry.
* **⚡ Auto-Filtering Optimization (Early GREEN Discard):** Legitimate players (**GREEN**) have negligible reconstruction error ($\text{MSE} < \theta_{\text{gray}}$) and are **immediately discarded from memory** to save server CPU and keep match tickrate latency $< 1\text{ms}$.
* **Reporting:** Only anomalous players (**GRAY** and **RED**) are reported forward to Stage 4.

### Detailed Stage 2 Python Code:

```python
from cds import ActiveAnomalyDetector
import numpy as np

# 1. Initialize detector with standard scaling & adaptive percentile derivation
stage2 = ActiveAnomalyDetector(
    auto_scale=True,
    percentile_gray=90.0, # Top 10% reconstruction error considered suspicious
    percentile_red=99.0,  # Top 1% reconstruction error considered critical exploit
)

# 2. Calibrate baseline using clean, verified gameplay telemetry frames
# Features: [Speed, Elevation Z-Delta, Damage Per Minute, Angular Aim Jerk]
clean_baseline_telemetry = np.array([
    [5.2, 0.10, 120.0, 1.25],
    [5.8, 0.12, 140.0, 1.40],
    [4.9, 0.08, 90.0,  0.95],
    [6.1, 0.15, 180.0, 1.80],
    [5.4, 0.11, 110.0, 1.15],
], dtype=np.float32)

# Train the Deep Autoencoder baseline
stage2.train_baseline(clean_baseline_telemetry, epochs=30, batch_size=8)
print(f"Adaptive Thresholds Derived -> GRAY: {stage2.threshold_gray:.4f}, RED: {stage2.threshold_red:.4f}")

# 3. Stream real-time match ticks for active players in an ongoing game
live_match_telemetry = np.array([
    [5.3, 0.11, 125.0, 1.20], # Normal player -> Discarded immediately (GREEN)
    [9.5, 0.45, 310.0, 4.20], # Moderate anomaly (micro-smoothing / recoil hack) -> GRAY
    [48.0, 25.0, 950.0, 18.5], # Blatant speedhack / super-jump / teleport -> RED
], dtype=np.float32)

active_player_ids = ["Player_Alice", "Player_Bob", "Player_Charlie"]

# 4. Evaluate telemetry
live_telemetry_results = stage2.evaluate_telemetry(live_match_telemetry, player_ids=active_player_ids)

# Notice: 'Player_Alice' was automatically DROPPED from active tracking to save memory!
print("GRAY Roster (Suspicious Kinematics):", live_telemetry_results["rosters"]["GRAY"]) # ['Player_Bob']
print("RED Roster  (Blatant Speed/Flyhacks):", live_telemetry_results["rosters"]["RED"])  # ['Player_Charlie']
```

---

## 🕵️ Step 5: Stage 3 — Agentic Profile Inspector (Seller Intelligence)

Many aggressive cheaters monetize their hacks by putting contact information (Discord, Telegram, WhatsApp, "DM for cheat") directly in their profile bio, username, or clan tag.

* **Anti-Obfuscation NLP:** Normalizes Unicode homoglyphs (`а` $\rightarrow$ `a`, `0` $\rightarrow$ `o`) and detects evasion patterns.
* **Safety Invariant:** A user profile alone **CANNOT** definitively ban a player. Therefore, Stage 3 outputs **ONLY GREEN and GRAY** (never direct `RED`).

```python
from cds import AgenticProfileInspector

stage3 = AgenticProfileInspector()

# Extract user profiles from your game database
profiles = [
    {
        "player_id": "Player_Alice",
        "nickname": "EagleEye",
        "clan_tag": "[LEGIT]",
        "bio": "Casual player having fun with friends in Battleground!"
    },
    {
        "player_id": "Player_Bob",
        "nickname": "ShadowTrader",
        "clan_tag": "[VIP]",
        "bio": "DM t.me/undetected_cheats for safe aimbot and radar ESP" # Seller signal!
    },
]

profile_results = stage3.inspect_profiles(profiles)
print("Stage 3 GREEN (Legitimate):", profile_results["rosters"]["GREEN"]) # ['Player_Alice']
print("Stage 3 GRAY  (Suspect Seller):", profile_results["rosters"]["GRAY"]) # ['Player_Bob']
```

---

## ⚖️ Step 6: Stage 4 — Pipeline Orchestrator & Multi-Model Consensus

Stage 4 runs all three detectors simultaneously and cross-evaluates their `GRAY` lists:

```
+-----------------------------------------------------------------------------------+
|                            STAGE 4 CONSENSUS MATRIX                               |
+-----------------------------------------------------------------------------------+
|  1. Direct RED Rule:                                                              |
|     Stage 1 is RED OR Stage 2 is RED                  ==> Final Verdict: RED      |
|                                                                                   |
|  2. The 3-GRAY Promotion Rule:                                                    |
|     Stage 1 is GRAY AND Stage 2 is GRAY AND Stage 3 is GRAY ==> Promote to RED!  |
|                                                                                   |
|  3. The 2-GRAY Retention Rule:                                                    |
|     Flagged as GRAY in only 1 or 2 models             ==> Retain in GRAY          |
|                                                           (Monitor Queue)         |
|                                                                                   |
|  4. Nominal Clean Rule:                                                           |
|     No red flags, normal telemetry                    ==> Final Verdict: GREEN    |
+-----------------------------------------------------------------------------------+
```

### Complete Orchestrator & Studio Callback Code:

```python
from cds import PipelineOrchestrator

# Define studio moderation callbacks
def studio_ban_cheater(player_id, audit_info):
    # Studio API call: disconnect player and issue HWID ban
    print(f"🚨 STUDIO ACTION: Banning {player_id}. Reason: {audit_info['reason']}")

def studio_monitor_suspect(player_id, audit_info):
    # Studio API call: increase tickrate sampling and record match demo
    print(f"⚠️ STUDIO ACTION: Placing {player_id} in high-tick 128Hz monitor queue.")

def studio_allow_player(player_id, audit_info):
    # Nominal player continues normal matchmaking
    pass

# Initialize orchestrator with moderation callbacks
orchestrator = PipelineOrchestrator(
    stage1_detector=stage1,
    stage2_detector=stage2,
    stage3_inspector=stage3,
    on_green_action=studio_allow_player,
    on_gray_action=studio_monitor_suspect,
    on_red_action=studio_ban_cheater,
)

# Harmonize all outputs into final verified rosters
final_verdict = orchestrator.harmonize_rosters(
    all_player_ids=["Player_Alice", "Player_Bob", "Player_Charlie"],
    stage1_rosters=classification_result["rosters"],
    stage2_rosters=live_telemetry_results["rosters"],
    stage3_rosters=profile_results["rosters"],
    match_id="MATCH_BATTLEGROUND_9021",
)

print("\n--- FINAL CDS CONSENSUS REPORT ---")
print("GREEN (Clean / Free)    :", final_verdict["rosters"]["GREEN"])
print("GRAY  (Soft Monitor)    :", final_verdict["rosters"]["GRAY"])
print("RED   (Confirmed Ban)   :", final_verdict["rosters"]["RED"])
```

---

## 🛡️ Developer Handover & Studio Responsibilities

Once CDS returns the final classified rosters, **you (the game developer) take action according to your studio policies**. CDS carries no moderation liability:

| Classification | Meaning | Recommended Game Studio Action |
| :---: | :--- | :--- |
| **`GREEN`** | **Clean Player** | **Free:** Player continues normal matchmaking without friction. |
| **`GRAY`** | **Suspicious Player** | **Monitor:** Increase server tick sampling (e.g. 128Hz), record match replay demo, or place in soft trust-factor queue. |
| **`RED`** | **Confirmed Cheater** | **Ban / Quarantine:** Immediate disconnect, account ban, HWID blacklisting, or route to cheater-only shadow lobbies. |
