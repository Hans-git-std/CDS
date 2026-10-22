# 📐 CDS Technical Architecture & Systems Specification

This document details the formal technical architecture for the **Cheat Detection System (CDS)**, specifying data structures, feature scaling equations, telemetry streaming protocols, and the Stage 4 consensus resolution engine.

---

## 1. System Topology & Pipeline Overview

CDS is structured around a **4-stage decoupled processing architecture** designed for high-concurrency multiplayer titles (such as 100-player Battleground games):

```
+---------------------------------------------------------------------------------------------------+
|                                   DATA INGESTION BOUNDARIES                                       |
|                                                                                                   |
|    +-----------------------------+                     +-------------------------------------+    |
|    | Historical Game Database    |                     | Dedicated Game Server Instances     |    |
|    | (PostgreSQL / Redis / Mongo)|                     | (Live Match 64-128Hz Simulation)    |    |
|    +-----------------------------+                     +-------------------------------------+    |
|                   |                                                       |                       |
|                   v (Historical Records)                                  v (gRPC Telemetry)      |
|    +-----------------------------+                     +-------------------------------------+    |
|    | Stage 1: Passive NLP Engine |                     | Stage 2: Active Anomaly Engine      |    |
|    | • Feature Scaling & Tokens  |                     | • Movement speed, Elevation/Height  |    |
|    | • Cold-Start Training Mode  |                     | • Real-time DPM, Headshot Rate      |    |
|    | • Outputs: GREEN, GRAY, RED |                     | • Discards GREEN -> GRAY / RED      |    |
|    +-----------------------------+                     +-------------------------------------+    |
|                   |                                                       |                       |
|                   +-----------------------+       +-----------------------+                       |
|                                           |       |                                               |
|                                           v       v                                               |
|    +-----------------------------+   +-------------------------------------------------------+    |
|    | Player Profile & Social DB  |   | Stage 4: Central Orchestrator & Consensus Engine      |    |
|    | (Bio, Nickname, Clan Tags)  |   | • Coordinates simultaneous model execution            |    |
|    +-----------------------------+   | • Aggregates & routes cross-model GRAY lists          |    |
|                   |                  | • 3-GRAY Promotion Rule: 3x GRAY ===> RED!            |    |
|                   v (Profile Data)   | • 2-GRAY Retention Rule: 2x GRAY ===> Keep in GRAY    |    |
|    +-----------------------------+   +-------------------------------------------------------+    |
|    | Stage 3: Agentic Profile    |                                |                               |
|    |   Inspector                 |                                |                               |
|    | • Detects seller handles    |                                v                               |
|    | • Discord / Telegram regex  |   +-------------------------------------------------------+    |
|    | • Outputs: GREEN / GRAY only|   | Final Classified Rosters: [ GREEN | GRAY | RED ]      |    |
|    +-----------------------------+   | Developer Handover: Free | Monitor | Ban              |    |
|                   |                  +-------------------------------------------------------+    |
|                   +-----------------------------------------------+                               |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Stage-by-Stage Specifications

### 2.1 Stage 1: Passive Detector (Historical Game Database)
The Passive Detector operates periodically (e.g. daily batch or post-match aggregation) against the game database.

#### Feature Scaling:
Features are normalized against empirical population limits:
* **Win Rate ($w$):** $w_{\text{norm}} = \min\left(\frac{w}{0.50}, 2.0\right)$
* **K/D Ratio ($k$):** $k_{\text{norm}} = \min\left(\frac{k}{10.0}, 2.0\right)$
* **Headshot Ratio ($h$):** $h_{\text{norm}} = \min\left(\frac{h}{0.75}, 2.0\right)$
* **Damage Per Match ($d$):** $d_{\text{norm}} = \min\left(\frac{d}{2000.0}, 2.0\right)$

#### Semantic Serialization:
Normalized values are converted to structured tokens for the language model:
```
<PLAYER_ID:P102> WIN_RATE_NORM:0.76 KD_NORM:0.48 HS_NORM:0.64 DMG_NORM:0.49
```

#### Cold-Start Training Mode:
When initialized, the developer supplies an Answer Key containing binary labels:
$$\mathcal{D}_{\text{train}} = \{(x_i, y_i) \mid y_i \in \{\text{GREEN}, \text{RED}\}\}$$
Ground-truth contains **no intermediate GRAY**. During inference, the continuous model score $S_1 \in [0, 1]$ partitions players:
$$\text{Verdict}_{S1}(x) = \begin{cases} \text{GREEN} & \text{if } S_1 < 0.35 \\ \text{GRAY} & \text{if } 0.35 \le S_1 < 0.75 \\ \text{RED} & \text{if } S_1 \ge 0.75 \end{cases}$$

---

### 2.2 Stage 2: Active Detector (Real-Time Live Telemetry)
The Active Detector evaluates streaming tick data from dedicated game servers.

#### Real-Time Telemetry Metrics:
1. **Kinematic Movement Speed ($v$):**
   $$v = \frac{\sqrt{\Delta x^2 + \Delta y^2}}{\Delta t}$$
   Threshold: If $v > 1.8 \cdot v_{\text{sprint\_max}}$, flag instant RED (Speed hack).
2. **Elevation / Z-Axis Velocity ($v_z$):**
   Detects fly-hacks or artificial hovering when terrain height gradient $\nabla Z_{\text{terrain}} \approx 0$.
3. **Damage Per Minute (DPM) & Headshot Rate:**
   Flags impossible burst rates (e.g., $DPM > 2700$ with $HS\% > 80\%$).
4. **Micro-Aim Snapping:**
   Measures angular jerk ($\frac{d^3\theta}{dt^3}$) and discontinuous velocity changes.

#### Filtering Logic:
* **GREEN Players:** Discarded immediately without database logging to conserve server memory and CPU.
* **GRAY & RED Players:** Emitted to the streaming bus for Stage 4 ingestion.

---

### 2.3 Stage 3: Agentic Profile Inspector (Seller Intelligence)
Aggressive cheat users frequently utilize their public gamer profiles to sell scripts, mod menus, and private configs.

#### Inspection Scope:
* `nickname`
* `clan_tag`
* `bio_status`
* `external_social_handles`

#### Pattern & Keyword Detection:
* Keywords: `cheat`, `hack`, `aimbot`, `esp`, `mod menu`, `vip config`, `undetected`, `script`.
* Communication Platforms: `t.me/`, `telegram`, `discord.gg`, `dc:`, `whatsapp`, `wa.me`.

#### Safety Invariant:
A player's bio text alone **cannot definitively trigger a permanent ban**. Therefore:
$$\text{Output}_{S3} \in \{\text{GREEN}, \text{GRAY}\}$$
(Stage 3 never emits RED directly).

---

### 2.4 Stage 4: Central Pipeline Orchestrator & Consensus Engine

Stage 4 unifies the independent streams using the **Cross-Model Consensus Matrix**:

Let $S_1(p), S_2(p), S_3(p)$ be the tier outputs for player $p$.

#### Consensus Rules:
1. **Direct RED Rule:**
   $$\text{FinalTier}(p) = \text{RED} \quad \text{if } S_1(p) = \text{RED} \lor S_2(p) = \text{RED}$$

2. **The 3-GRAY Promotion Rule:**
   $$\text{FinalTier}(p) = \text{RED} \quad \text{if } S_1(p) = \text{GRAY} \land S_2(p) = \text{GRAY} \land S_3(p) = \text{GRAY}$$

3. **The 2-GRAY Retention Rule:**
   $$\text{FinalTier}(p) = \text{GRAY} \quad \text{if } \sum_{i=1}^3 \mathbb{I}(S_i(p) = \text{GRAY}) \in \{1, 2\} \land \text{FinalTier}(p) \ne \text{RED}$$

4. **Nominal Baseline Rule:**
   $$\text{FinalTier}(p) = \text{GREEN} \quad \text{otherwise}$$

---

## 3. Developer Handover & API Schema

The orchestrator outputs a structured payload for the game developer's administrative backend:

```json
{
  "timestamp": "2026-10-23T01:50:00Z",
  "match_id": "BATTLEGROUND_MATCH_8819",
  "summary": {
    "total_players": 100,
    "green_count": 92,
    "gray_count": 6,
    "red_count": 2
  },
  "rosters": {
    "GREEN": ["P101", "P105", "..."],
    "GRAY": ["P103", "P108", "..."],
    "RED": ["P102", "P104"]
  },
  "audit_trail": {
    "P102": {
      "final_tier": "RED",
      "reason": "3_GRAY_PROMOTION",
      "stage1_status": "GRAY",
      "stage2_status": "GRAY",
      "stage3_status": "GRAY",
      "gray_overlap_count": 3
    }
  },
  "developer_actions": {
    "GREEN": "Free / Allow normal play. Telemetry archived.",
    "GRAY": "Monitor / Increase tickrate to 128Hz, record full demo, queue for review.",
    "RED": "Ban or Quarantine / Immediate disconnect, HWID ban, or route to shadow-lobbies."
  }
}
```
