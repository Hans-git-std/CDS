# 🎮 Battleground Implementation Guide (`battleground-implementation.md`)

Welcome to the **CDS (Cheat Detection System) Battleground Implementation Guide**.  
This document is designed for game developers integrating CDS into modern multiplayer Battle Royale / Battleground titles (e.g., tactical shooters, open-world survival games, 100-player battle arenas).

---

## 📌 Executive Integration Overview

The CDS system operates as a hybrid 4-stage intelligence pipeline across two development phases:
* **Stage 1 (Passive Detector):** Analyzes historical player profile databases using NLP with feature scaling.
* **Stage 2 (Active Detector):** Analyzes real-time player telemetry during live matches using anomaly detection.
* **Stage 3 (Agentic Profile Inspector):** Inspects user profiles, nicknames, and bio descriptions for cheat-seller contact details using LLM agentic reasoning.
* **Stage 4 (Central Pipeline Orchestrator):** Harmonizes all three models, performs cross-model GRAY list routing, and promotes multi-gray suspects to RED.

```
       +---------------------------------------------------------------------------------+
       |                              DEVELOPER'S GAME BACKEND                           |
       +---------------------------------------------------------------------------------+
                 | (Historical Stats)                         | (Live Telemetry)
                 v                                            v
     +-----------------------+                    +-----------------------+
     |  STAGE 1: PASSIVE NLP |                    | STAGE 2: ACTIVE ANOMALY|
     |  • Win rate, K/D      |                    | • Speed, Height, DPM  |
     |  • Headshot %, Kills  |                    | • Real-time Aim & K/D |
     +-----------------------+                    +-----------------------+
         | GREEN / GRAY / RED                         | (Discards Green) -> GRAY / RED
         +----------------------------+  +------------+
                                      |  |
                                      v  v
                         +-----------------------------+
                         | STAGE 4: PIPELINE &         | <--- [STAGE 3: AGENTIC PROFILE]
                         | CONSENSUS ORCHESTRATOR      |      • Pulls profile bio / contacts
                         |                             |      • Detects seller tags (Telegram/DC)
                         | • Cross-evaluates GRAY lists|      • Returns: GREEN / GRAY
                         | • 3x GRAY  ==> RED          |
                         | • 2x GRAY  ==> Keep GRAY    |
                         +-----------------------------+
                                        |
                 +----------------------+----------------------+
                 |                      |                      |
                 v                      v                      v
             [ GREEN ]              [ GRAY ]               [ RED ]
             Action: Free       Action: Monitor        Action: Ban / Kick
         (Dev responsibility) (Dev responsibility)   (Dev responsibility)
```

---

## 🚀 Step 1: Stage 1 — Passive Detector (Game DB & Feature Scaling)

### 1.1 Attach Game Database
Extract historical player summary statistics from your game database (PostgreSQL, MongoDB, Redis, or MySQL).

**Required Battleground Features:**
* `win_rate`: Percentage of matches won (0.0 – 1.0)
* `kd_ratio`: Overall Kill-to-Death ratio
* `total_matches`: Lifetime matches played
* `total_kills`: Lifetime kill count
* `headshot_rate`: Ratio of headshot kills to total kills (0.0 – 1.0)
* `damage_per_match`: Average damage inflicted per round
* `account_age_days`: Age of the user account in days

### 1.2 Feature Scaling & NLP Serialization
CDS formats your scaled numerical stats into semantic feature tokens for the NLP model:
```
"PLAYER_STAT: matches=42 kd=18.4 win_rate=0.78 headshot=0.82 dpm=1450 account_age=2d"
```

### 1.3 Training Mode vs. Inference Mode (First Time Setup)
> [!IMPORTANT]
> When initializing CDS for the first time on your game, run in **Training Mode**.  
> You must provide an **Answer Key** containing only known **GREEN** (legitimate verified players) and **RED** (confirmed previously banned cheaters).  
> In ground-truth training, there is **no GRAY tier**—the model learns the boundary between clean and banned behavior to infer suspicious intermediate GRAY cases during live inference.

#### Python Code Example (Stage 1):
```python
from cds.stage1_passive_nlp import PassiveNLPDetector

detector = PassiveNLPDetector()

# 1. First Time: Train with your Ground Truth Answer Key
training_data = [
    {"player_id": "P101", "features": {"kd_ratio": 1.2, "win_rate": 0.12, "headshot_rate": 0.22, "total_matches": 350}, "label": "GREEN"},
    {"player_id": "P999", "features": {"kd_ratio": 24.5, "win_rate": 0.89, "headshot_rate": 0.94, "total_matches": 15}, "label": "RED"}
]
detector.train(training_data)

# 2. Live Inference: Classify player batch from Game DB
results = detector.evaluate_batch(game_db_records)
# Returns:
# results["GREEN"] -> List of clean player IDs
# results["GRAY"]  -> List of suspicious player IDs
# results["RED"]   -> List of definite cheater IDs
```

---

## ⚡ Step 2: Stage 2 — Active Detector (Real-Time In-Game Telemetry)

While Stage 1 looks at cold database history, **Stage 2 runs concurrently and independently during live battleground matches**.

### 2.1 Real-Time In-Game Telemetry Inputs
Stream active telemetry from your dedicated match servers:
* `movement_speed`: Instantaneous horizontal velocity (detects speed hacks).
* `player_height`: Vertical elevation / Z-coordinate deltas (detects fly hacks and high-jump exploits).
* `damage_per_minute (DPM)`: Real-time damage output in the active match.
* `active_kd`: Current match K/D ratio.
* `active_headshot_rate`: Current match headshot percentage.
* `micro_aim_delta`: Frame-by-frame mouse angular adjustment and snap variance (detects aimbot micro-adjustments).

### 2.2 Behavior & Output
* Immediately filters out **GREEN** (clean players are dropped from high-frequency checks to save CPU).
* Emits only **GRAY** (anomalous behavior requiring verification) and **RED** (blatant physical impossibilities, e.g., speed > 300% or instant 180° headshot snaps).

#### Python Code Example (Stage 2):
```python
from cds.stage2_active_anomaly import ActiveAnomalyDetector

active_detector = ActiveAnomalyDetector()

# Stream real-time tick data from live battleground match
telemetry_event = {
    "player_id": "P304",
    "match_id": "M_BATTLEGROUND_89",
    "movement_speed": 42.5,          # Normal max sprint is 15.0 m/s
    "player_height": 180.2,          # Normal terrain height is 15.0 m
    "active_dpm": 2800.0,
    "active_headshot_rate": 0.95,
    "micro_aim_snap": True
}

verdict = active_detector.evaluate_tick(telemetry_event)
# Verdict returns: 'GRAY' or 'RED' (GREEN is discarded from alerting)
```

---

## 🕵️ Step 3: Stage 3 — External Agentic Profile Intelligence

### 3.1 The Problem
Many aggressive cheaters do not just play—they **sell their cheat formulas and tools**. They advertise contact channels directly in their player profiles, bio descriptions, status text, and usernames (e.g., `"DM for cheat DC: hacklord#123"`, `"Tele: @ez_win_cheats"`, `"whatsapp hacks link"`).

### 3.2 Agentic Reasoning
Stage 3 pulls user profile metadata from the database and runs an agentic LLM classifier:
* Inspects: `username`, `status_bio`, `clan_tag`, `external_links`, `signature`.
* Looks for: Obfuscated contact information, seller phrasing, discord handles, telegram invite codes, payment links.
* **Important Safety Boundary:** A profile alone **cannot definitively brand a player RED**. Therefore, Stage 3 outputs **only GREEN or GRAY**.

#### Python Code Example (Stage 3):
```python
from cds.stage3_agentic_profile import AgenticProfileInspector

inspector = AgenticProfileInspector()

profile_data = {
    "player_id": "P405",
    "nickname": "xX_Destroyer_Xx",
    "bio": "Private undetected aimbot & ESP available. Join t.me/fast_cheats_apex",
    "clan_tag": "[HACK]"
}

verdict = inspector.inspect_profile(profile_data)
# Verdict returns: 'GRAY' (Suspicious) or 'GREEN' (Nominal)
```

---

## 🔄 Step 4: Stage 4 — Pipeline Orchestrator & Consensus Engine

Stage 4 is the brain that balances, schedules, and unifies all three independent models:

### 4.1 Cross-Model GRAY Routing & Consensus Logic
1. **Direct RED Rule:** If Stage 1 or Stage 2 outputs `RED`, the player is immediately categorized as **RED**.
2. **The 3-GRAY Promotion Rule:** If a player is marked as **GRAY** across **all three models** (Stage 1 Passive, Stage 2 Active, AND Stage 3 Profile Agent), Stage 4 **automatically promotes the player to RED**.
3. **The 2-GRAY Retention Rule:** If a player is marked as **GRAY** by only 1 or 2 models, they **remain in GRAY** (queued for elevated monitoring and telemetry capture).
4. **Clean Rule:** Players evaluated as GREEN across active checks remain **GREEN**.

```
+-----------------------------------------------------------------------------------------+
|                               STAGE 4 CONSENSUS MATRIX                                  |
+--------------------+--------------------+--------------------+--------------------------+
| Stage 1 (Passive)  | Stage 2 (Active)   | Stage 3 (Profile)  | FINAL RESOLUTION         |
+--------------------+--------------------+--------------------+--------------------------+
| RED                | Any                | Any                | ===> RED (Instant Flag)  |
| Any                | RED                | Any                | ===> RED (Instant Flag)  |
| GRAY               | GRAY               | GRAY               | ===> RED (3-Gray Promote)|
| GRAY               | GRAY               | GREEN              | ===> GRAY (Retain/Watch) |
| GRAY               | GREEN              | GRAY               | ===> GRAY (Retain/Watch) |
| GREEN              | GRAY               | GREEN              | ===> GRAY (Retain/Watch) |
| GREEN              | GREEN              | GREEN              | ===> GREEN (Clean)       |
+--------------------+--------------------+--------------------+--------------------------+
```

#### Python Code Example (Stage 4 Orchestrator):
```python
from cds.stage4_orchestrator import PipelineOrchestrator

orchestrator = PipelineOrchestrator(
    stage1_detector=detector,
    stage2_detector=active_detector,
    stage3_inspector=inspector
)

# Run full cross-model assessment
final_lists = orchestrator.process_batch(players_batch)

print("GREEN Players (Clean):", len(final_lists["GREEN"]))
print("GRAY Players (Monitor):", len(final_lists["GRAY"]))
print("RED Players (Cheater):", len(final_lists["RED"]))
```

---

## 🛡️ Developer Responsibility & Enforcement Handover

Once CDS returns the final `GREEN`, `GRAY`, and `RED` rosters, the developer takes over with their custom game policies:

| CDS Output Tier | Recommended Developer Action | Policy Notes |
| :--- | :--- | :--- |
| **`GREEN`** | **Free / No Restriction** | Player plays normally. Low-frequency telemetry archiving. |
| **`GRAY`** | **Monitor / High-Tick Telemetry** | Increase server tick recording to 128Hz, record demo replay, route to spectator review queue, or place in soft trust-factor matchmaking. |
| **`RED`** | **Ban / Quarantine** | Immediate match disconnect, HWID/account ban, damage nullification, or silent placement in shadow-lobbies (cheaters vs cheaters). |

> **CDS Disclaimer:** CDS provides high-fidelity behavioral classification. Enforcement actions (banning, matchmaking routing, penalty duration) are solely executed at the game studio's discretion.
