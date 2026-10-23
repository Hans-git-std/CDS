# 🛡️ CDS: Cheat Detection System

<p align="center">
  <img src="https://img.shields.io/badge/Framework-Cheat_Detection_System_(CDS)-0F2942?style=for-the-badge&logo=shield&logoColor=white" alt="CDS System" />
  <img src="https://img.shields.io/badge/ML_Engine-TensorFlow_2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white" alt="TensorFlow" />
  <img src="https://img.shields.io/badge/Status-Production_Ready-10B981?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/License-Proprietary_(View--Only)-E11D48?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <strong>A Developer-Implemented Multi-Stage Anti-Cheat Framework Powered by TensorFlow</strong><br>
  <em>Engineered for modern multiplayer titles (e.g. Battlegrounds, Battle Royales, competitive shooters) using Passive NLP, Active Telemetry Autoencoders, and Agentic Profile Intelligence.</em>
</p>

---

## 📌 Core Architecture Principles

1. **Features are Decided by the Developer (YOU), Not by Us:**  
   CDS is completely feature-agnostic. Whether your game tracks 4 features or 40 features, the models dynamically adapt to your input dimensions. We guide you on feature selection, but you retain full control over your telemetry.
2. **`$$$ info $$$` Marker Convention:**  
   Every developer-configurable section, custom feature list, and studio integration point is explicitly marked between **`$$$ info $$$`** markers (e.g. `$$$ YOUR_CHOSEN_DATABASE_FEATURES $$$`, `$$$ YOUR_LIVE_TELEMETRY_STREAM $$$`, `$$$ YOUR_BAN_CALLBACK $$$`). This makes it immediately obvious where you plug in your game data!
3. **Powered by TensorFlow:**  
   Uses standard `tf.keras.Sequential` architectures for supervised historical feature classification and deep Autoencoders for real-time anomaly detection.
4. **Designed for Easy Implementation:**  
   Even a beginner or junior developer can integrate CDS into their game in a single afternoon by following [**`battleground-implementation.md`**](battleground-implementation.md).

---

## 🗺️ The 2-Stage Strategic Roadmap

* **Stage 1 (Core Analogy & Engine — *Current Development*):**  
  The core open framework: TensorFlow Sequential models, Autoencoder reconstruction error math, profile inspection heuristics, and multi-model consensus logic.
* **Stage 2 (Battleground Implementation — *Next Step*):**  
  Integration reference for **Modern Online Battleground titles** (e.g., 100-player Battle Royale games) covering parachuting elevation, vehicle velocities, and high-tick gunplay kinematics. See [**`battleground-implementation.md`**](battleground-implementation.md).

---

## ⚙️ How the 4 Internal Stages Work

```
+---------------------------------------------------------------------------------------------------+
|                                     CDS 4-STAGE ARCHITECTURE                                      |
+--------------------------+---------------------------+--------------------------------------------+
| STAGE 1: PASSIVE NLP     | STAGE 2: ACTIVE ANOMALY   | STAGE 3: PROFILE AGENT                     |
| (Game Database Stats)    | (Live Match Telemetry)    | (Cheat Seller Intelligence)                |
| • TensorFlow Sequential  | • TensorFlow Autoencoder  | • Profile Bio, Nickname, Clan Tags         |
| • Trained with Answer Key| • Evaluates live in-game  | • Scans for Discord / Telegram seller tags |
|   (GREEN=0, RED=1 only)  |   telemetry               | • Outputs: GREEN / GRAY only               |
| • Outputs: GRN / GRY / RED| • Drops GREEN early      |   (Profiles alone cannot be definitely RED)|
|                          | • Outputs: GRAY / RED     |                                            |
+--------------------------+---------------------------+--------------------------------------------+
                                          |
                                          v
+---------------------------------------------------------------------------------------------------+
|                      STAGE 4: CENTRAL PIPELINE ORCHESTRATOR & CONSENSUS ENGINE                    |
| • Runs all 3 models simultaneously and balances compute resources.                                |
| • Routes the GRAY lists across models to decide final promotions.                                 |
| • 3-GRAY Promotion Rule: Flagged as GRAY across ALL 3 models  ===> Promoted to RED!               |
| • 2-GRAY Retention Rule: Flagged as GRAY in only 1 or 2       ===> Retained in GRAY (Monitor).    |
+---------------------------------------------------------------------------------------------------+
                                          |
                                          v
                 [ Developer Handover: Free (Green) | Monitor (Gray) | Ban (Red) ]
```

### Stage 1: Passive Detector (TensorFlow Sequential)
* **Data Source:** Historical game database (Win rate, KD, Headshots, Matches, etc. — chosen by you).
* **Cold-Start Training Mode:** When first setting up the repo, the developer supplies an **Answer Key** containing known **GREEN** (clean players) and **RED** (banned cheaters). In ground truth training, there is **no intermediate GRAY**—the model learns the clean boundary and infers suspicious **GRAY** players during live inference.
* **Output:** Tri-state roster: `GREEN`, `GRAY`, `RED`.

### Stage 2: Active Detector (TensorFlow Autoencoder)
* **Data Source:** Real-time live match telemetry (Speed, elevation/height, live DPM, aim-snap deltas — chosen by you).
* **Deep Autoencoder:** Trained on legitimate clean gameplay to reconstruct natural movement. High reconstruction error indicates an active kinematic cheat.
* **Resource Optimization:** Clean players (**GREEN**) are **automatically removed and discarded immediately** to save server CPU. Reports only `GRAY` and `RED`.
* **Independence:** Runs concurrently and independently from Stage 1.

### Stage 3: Agentic Profile Inspector (Seller Intelligence)
* **The Insight:** Many cheat users advertise and sell their private hack scripts, mod menus, or configs by putting contact info (Discord, Telegram, WhatsApp) in their profile bio or username.
* **Inspection:** Scans profile metadata for commercial seller patterns and communication handles.
* **Safety Invariant:** A profile text alone **cannot prove active cheating**. Therefore, Stage 3 outputs **ONLY GREEN or GRAY** (never RED).

### Stage 4: Central Pipeline Orchestrator & Consensus Engine
* Coordinates all 3 models simultaneously.
* **The 3-GRAY Promotion Rule:** If a player is marked as **GRAY across ALL THREE models**, Stage 4 **automatically promotes them to RED**!
* **The 2-GRAY Retention Rule:** If marked as **GRAY in only 1 or 2 models**, they **remain in GRAY** (monitor queue).
* Direct REDs from Stage 1 or Stage 2 remain **RED**.

---

## ⚖️ The Consensus Matrix

| Stage 1 (Passive DB) | Stage 2 (Active Telemetry) | Stage 3 (Profile Bio) | Final Resolution | Action & Explanation |
| :---: | :---: | :---: | :---: | :--- |
| **RED** | *Any* | *Any* | 🟥 **RED** | **Direct Red Flag:** Flagged by historical DB statistics. |
| *Any* | **RED** | *Any* | 🟥 **RED** | **Direct Red Flag:** Impossible speed/elevation/aim in live match. |
| **GRAY** | **GRAY** | **GRAY** | 🟥 **RED** | **3-Gray Promotion:** Flagged across all 3 independent vectors $\rightarrow$ **Promoted to RED**! |
| **GRAY** | **GRAY** | **GREEN** | 🟨 **GRAY** | **2-Gray Retention:** 2 flags present $\rightarrow$ Retained in monitor queue. |
| **GRAY** | **GREEN** | **GRAY** | 🟨 **GRAY** | **2-Gray Retention:** Retained in monitor queue. |
| **GREEN** | **GRAY** | **GREEN** | 🟨 **GRAY** | **1-Gray Retention:** Single anomaly $\rightarrow$ Retained in soft watch. |
| **GREEN** | **GREEN** | **GREEN** | 🟩 **GREEN** | **Nominal Baseline:** Verified clean player. |

---

## 💡 Feature Selection Guide for Developers

You decide which features to pass into the detectors! Here are recommended types of features:

| Detector Stage | Recommended Feature Types (Examples) | How to Prepare |
| :--- | :--- | :--- |
| **Stage 1 (Passive DB)** | Cumulative Win Rate, Lifetime K/D, Headshot %, Damage per match, Account age | CDS built-in `FeatureScaler` automatically scales features to $[0.0, 1.0]$. |
| **Stage 2 (Active Telemetry)** | Horizontal movement speed, vertical height delta, real-time DPM, angular aim jerk | Normalize tick values relative to maximum natural sprint/aim limits. |
| **Stage 3 (Profile Agent)** | Profile status bio, custom nickname, clan tag | Raw text strings from user profile table. |

---

## ⚡ Quickstart Example (Python)

```python
from cds import (
    PassiveNLPDetector,
    ActiveAnomalyDetector,
    AgenticProfileInspector,
    PipelineOrchestrator
)
import numpy as np

# 1. Initialize models with automatic feature scaling
stage1 = PassiveNLPDetector(auto_scale=True)
stage2 = ActiveAnomalyDetector(auto_scale=True)
stage3 = AgenticProfileInspector()
orchestrator = PipelineOrchestrator(stage1, stage2, stage3)

# 2. Train Stage 1 with your Ground-Truth Answer Key (0=GREEN, 1=RED)
# $$$ [YOUR_DATABASE_TRAINING_SAMPLES_AND_ANSWER_KEY] $$$
X_db_train = np.array([$$$ [0.05, 0.10] $$$, $$$ [0.08, 0.12] $$$, $$$ [0.92, 0.95] $$$], dtype=np.float32)
y_db_train = np.array([$$$ 0 $$$, $$$ 0 $$$, $$$ 1 $$$], dtype=np.float32)
stage1.train(X_db_train, y_db_train, epochs=25)

# 3. Train Stage 2 Autoencoder on clean gameplay telemetry
# $$$ [YOUR_NORMAL_CLEAN_GAMEPLAY_TELEMETRY] $$$
X_clean_telem = np.array([$$$ [0.20, 0.15] $$$, $$$ [0.25, 0.18] $$$], dtype=np.float32)
stage2.train_baseline(X_clean_telem, epochs=25)

# 4. Run full orchestrator on active players
final_results = orchestrator.harmonize_rosters(
    all_player_ids=$$$ ["P101", "P102"] $$$,
    stage1_rosters={"GREEN": ["P101"], "GRAY": ["P102"], "RED": []},
    stage2_rosters={"GRAY": ["P102"], "RED": []},
    stage3_rosters={"GREEN": ["P101"], "GRAY": ["P102"]},
)

# P102 was GRAY in all 3 models -> Automatically promoted to RED!
print("RED Banned Players:", final_results["rosters"]["RED"])
```

---

## 🛡️ Developer Handover & Enforcement Policy

CDS handles **threat detection and categorization**. The game developer executes moderation actions according to studio policy:

* **GREEN List:** The developer frees the player for normal matchmaking.
* **GRAY List:** The developer monitors the player (e.g. increase server tickrate to 128Hz, record full match demo, soft trust queue).
* **RED List:** The developer applies disciplinary actions (instant match disconnect, HWID/account ban, damage nullification, or shadow-lobbies).
* **Disclaimer:** CDS holds no liability or responsibility for game studio moderation decisions after delivering the classified rosters.

---

## 📂 Repository Layout

```
CDS/
├── README.md                                  # Designer overview & quickstart (You are here)
├── battleground-implementation.md             # Beginner-friendly integration tutorial
├── LICENSE                                    # Proprietary View-Only Evaluation License
├── Cheat_Detection_System_Specification.docx  # Full Microsoft Word engineering specification
├── generate_docs.py                          # Script to regenerate Word document
├── cds/                                       # Core Python package
│   ├── __init__.py                            # Package exports
│   ├── scaler.py                              # Feature scaling utilities (MinMax, Standard, Robust)
│   ├── passive_nlp.py                         # Stage 1: TensorFlow Sequential DB model
│   ├── active_anomaly.py                      # Stage 2: TensorFlow Autoencoder telemetry model
│   ├── agentic_profile.py                     # Stage 3: Profile & cheat-seller inspector
│   └── orchestrator.py                        # Stage 4: Orchestrator & 3-Gray consensus engine
├── examples/
│   └── quickstart_tutorial.py                 # Full beginner-friendly tutorial simulation
├── tests/
│   └── test_pipeline.py                       # Automated test suite (8 tests)
├── docs/
│   ├── ARCHITECTURE.md                        # Technical subsystem & TensorFlow architecture
│   └── ANALYSIS_AND_IMPROVEMENTS.md           # Engineering analysis, gaps & recommendations
└── .gitignore                                 # Git ignore configuration
```

---

## 🧪 Run the Tutorial & Automated Tests Locally

Run the complete 4-stage tutorial simulation with TensorFlow:

```powershell
cd D:\Project\CDS\examples
uv run --with tensorflow python quickstart_tutorial.py
```

Run the automated test suite:

```powershell
cd D:\Project\CDS
uv run --with tensorflow python -m unittest discover -s tests
```

---

## 🔒 License & Restrictions

**Copyright (c) 2026 The CDS Project. All rights reserved.**

Distributed under a strict **Proprietary & Confidential Source-Available View-Only License**.  
Viewing and evaluation permitted; copying, forking, redistribution, or unauthorized commercial use strictly prohibited.  
See [`LICENSE`](LICENSE) for full details.
