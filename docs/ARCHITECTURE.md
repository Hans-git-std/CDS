# 📐 CDS Technical Architecture & Systems Engineering

This document provides the formal technical specification for the **Cheat Detection System (CDS)**, detailing mathematical formulations, telemetry data structures, streaming pipelines, and multi-agent verification workflows.

---

## 1. High-Level System Topology

```
+---------------------------------------------------------------------------------------------------+
|                                      GAME CLIENT & SERVER TIERS                                   |
|                                                                                                   |
|   +-----------------------+              +----------------------------------------------------+   |
|   | Game Client (Player)  |              | Dedicated Game Server (Authoritative Tick Loop)    |   |
|   | • Unreliable Network  |              | • 64-128 Hz simulation                              |   |
|   | • Raw Input Events    | --gRPC/UDP-> | • High-resolution position & angle delta recording  |   |
|   | • Local Chat Buffer   |              | • Lightweight Jerk filter (<1ms overhead)          |   |
|   +-----------------------+              +----------------------------------------------------+   |
+-------------------------------------------------------------|-------------------------------------+
                                                              |
                                                    gRPC Telemetry Stream
                                                              v
+---------------------------------------------------------------------------------------------------+
|                                    CDS DISTRIBUTED INGESTION LAYER                                |
|                                                                                                   |
|   +-------------------------------------------------------------------------------------------+   |
|   | Apache Kafka Telemetry Clusters                                                           |   |
|   | • Topic: telemetry.player.kinematics (Partitioned by match_id)                           |   |
|   | • Topic: telemetry.gameplay.events (Partitioned by player_id)                             |   |
|   | • Topic: telemetry.social.reports (Partitioned by reporter_id)                            |   |
|   +-------------------------------------------------------------------------------------------+   |
+-------------------------------------------------------------|-------------------------------------+
                                                              |
                       +--------------------------------------+-------------------------------------+
                       |                                                                            |
                       v                                                                            v
+-----------------------------------------------+   +-----------------------------------------------+
|         LAYER 1: PASSIVE NLP PIPELINE         |   |        LAYER 2: ACTIVE KINEMATIC PIPELINE     |
|                                               |   |                                               |
| • Asynchronous stream worker                  |   | • Apache Flink stateful sliding window (3s)   |
| • RoBERTa semantic report classifier          |   | • Minimum Jerk biomechanical verification     |
| • Reporter credibility Bayesian updater       |   | • Crosshair-occlusion mutual information      |
| • Action-token sequence perplexity evaluator  |   | • Real-time isolation forest & autoencoder    |
+-----------------------------------------------+   +-----------------------------------------------+
                       |                                                             |
                       +--------------------------------------+----------------------+
                                                              |
                                                              v
+---------------------------------------------------------------------------------------------------+
|                                  CDS CENTRAL SCORING & FUSION HUB                                 |
|                                                                                                   |
| • Computes Combined Risk Score: R_total = w1*R_nlp + w2*R_kinematics + w3*R_history               |
| • If R_total >= 0.70: Trigger match replay extraction & dispatch to Layer 3                       |
| • Writes real-time feature snapshots to ClickHouse & Feast Feature Store                          |
+-------------------------------------------------------------|-------------------------------------+
                                                              |
                                            Trigger Match Dossier (Replay Slice)
                                                              v
+---------------------------------------------------------------------------------------------------+
|                                LAYER 3: AGENTIC VERIFICATION ENGINE                               |
|                                                                                                   |
|  +-----------------------------+  +-----------------------------+  +---------------------------+  |
|  | Kinematic Inspector Agent   |  | Spatial & Context Agent     |  | Verdict Arbiter Agent     |  |
|  | • Input sandbox replay      |  | • Audio cue correlation     |  | • Multi-agent consensus   |  |
|  | • Micro-jitter validation   |  | • Radar / callout awareness |  | • Bayesian confidence     |  |
|  | • Hardware flag audit       |  | • Line-of-sight analysis    |  | • Auto-dossier synthesis  |  |
|  +-----------------------------+  +-----------------------------+  +---------------------------+  |
+-------------------------------------------------------------|-------------------------------------+
                                                              |
                                               Enforcement API / Moderator Portal
                                                              v
+---------------------------------------------------------------------------------------------------+
| • Silent Shadow-Matchmaking (Cheater Pool)                                                        |
| • Automated Real-Time Damage Nullification / In-Game Disconnect                                   |
| • Human Moderator Dashboard with Replay Video + Telemetry Overlays                                |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Mathematical & Algorithmic Formulations

### 2.1 Layer 2: Kinematic Minimum Jerk Model
Human movement obeys Flash & Hogan's *Minimum Jerk Principle*, where motor control minimizes the total jerk (time derivative of acceleration) across any target trajectory:

$$J = \frac{1}{2} \int_0^T \left( \left(\frac{d^3 x}{dt^3}\right)^2 + \left(\frac{d^3 y}{dt^3}\right)^2 \right) dt$$

For a human performing a rapid aim snap (saccadic rotation) from angle $\theta_0$ to target angle $\theta_f$ over duration $T$, the angular trajectory $\theta(t)$ follows a 5th-order polynomial:

$$\theta(t) = \theta_0 + (\theta_f - \theta_0) \left( 10\left(\frac{t}{T}\right)^3 - 15\left(\frac{t}{T}\right)^4 + 6\left(\frac{t}{T}\right)^5 \right)$$

#### Anomaly Detection Conditions:
1. **Instantaneous Angular Jerk:** If $\left|\frac{d^3\theta}{dt^3}\right| > \tau_{\text{bio\_max}}$ where $\tau_{\text{bio\_max}}$ is the biological muscular limit for human hand/wrist motion.
2. **Bezier Smoothing Deviations:** Algorithmic smoothers that use constant velocity, quadratic Bezier curves, or linear interpolation fail the 5th-order smoothness test, yielding residuals:

$$R_{\text{jerk}} = \frac{1}{N} \sum_{i=1}^N \left| \theta_{\text{actual}}(t_i) - \theta_{\text{predicted\_jerk}}(t_i) \right| > \epsilon_{\text{threshold}}$$

### 2.2 Crosshair-to-Target Mutual Information (Occlusion Tracking)
To detect wallhacks (ESP), CDS computes the Mutual Information $I(X; Y)$ between the player's 2D screen crosshair trajectory $C(t)$ and the 3D-to-2D projected center-of-mass $E_j(t)$ of an occluded enemy behind geometry:

$$I(C; E_j) = \iint p(c, e_j) \log_2 \left(\frac{p(c, e_j)}{p(c)\, p(e_j)}\right) dc\, de_j$$

* **Legitimate Player:** $I(C; E_j) \approx 0$ when the enemy is fully occluded and unheralded by audio/radar.
* **Wallhack Player:** $I(C; E_j) \gg 0$, indicating unconscious or intentional tracking of geometry-occluded targets.

### 2.3 Layer 1: Action Sequence Perplexity
Let discrete player actions be tokenized as $a_1, a_2, \dots, a_T \in \mathcal{V}$. The sequence perplexity under an autoregressive language model $P_\theta$ trained on millions of legitimate player rounds is:

$$\text{PPL}(a_{1:T}) = \exp \left( -\frac{1}{T} \sum_{t=1}^T \log P_\theta(a_t \mid a_1, \dots, a_{t-1}) \right)$$

Sub-millisecond perfect decision loops produce high perplexity spikes relative to normal human reaction chains.

---

## 3. Data Structures & Telemetry Protocols

### 3.1 Kinematic Sample Packet (gRPC / Protobuf)

```protobuf
syntax = "proto3";

package cds.telemetry.v1;

message KinematicSample {
  uint64 match_id = 1;
  uint32 player_id = 2;
  uint64 tick_index = 3;
  double timestamp_ms = 4;
  
  // View Angles in Degrees (-180.0 to 180.0, -89.0 to 89.0)
  float yaw = 5;
  float pitch = 6;
  
  // High-Resolution Angular Velocities (deg/s)
  float yaw_velocity = 7;
  float pitch_velocity = 8;
  
  // Angular Acceleration & Jerk
  float angular_accel = 9;
  float angular_jerk = 10;
  
  // Controller / Mouse Input Raw Deltas
  int32 raw_mouse_dx = 11;
  int32 raw_mouse_dy = 12;
  
  // Game Context State Flags
  bool is_firing = 13;
  bool has_target_in_fov = 14;
  bool is_target_occluded = 15;
  float distance_to_target = 16;
}
```

### 3.2 Verification Incident Dossier

```protobuf
message IncidentDossier {
  string incident_id = 1;
  uint64 match_id = 2;
  uint32 suspect_player_id = 3;
  double trigger_timestamp = 4;
  
  float passive_nlp_risk_score = 5;
  float active_kinematic_risk_score = 6;
  
  repeated KinematicSample anomalous_ticks = 7;
  string replay_slice_url = 8;
  
  // Agentic Verification Findings
  string kinematic_agent_summary = 9;
  string spatial_context_summary = 10;
  float final_confidence_percentage = 11;
  
  enum ActionVerdict {
    NO_ACTION = 0;
    WATCHLIST = 1;
    SHADOW_MATCHMAKE = 2;
    MODERATOR_REVIEW = 3;
    INSTANT_BAN = 4;
  }
  ActionVerdict recommended_verdict = 12;
}
```

---

## 4. Layer 3 Multi-Agent Orchestration

The Agentic Verification Layer leverages a specialized multi-agent graph running in an isolated review cluster:

```
                  +--------------------------------+
                  |    Anomaly Alert Received      |
                  +--------------------------------+
                                  |
                                  v
                  +--------------------------------+
                  |  Replay Slice Extraction Tool  |
                  +--------------------------------+
                                  |
            +---------------------+---------------------+
            |                                           |
            v                                           v
+-----------------------+                   +-----------------------+
| Kinematics Agent      |                   | Spatial Context Agent |
| Tools:                |                   | Tools:                |
| - PhysicsSandbox()    |                   | - RaycastOcclusion()  |
| - MouseJitterFFT()    |                   | - AudioSoundmapQuery()|
| - JerkCurveFit()      |                   | - TeammateCalloutLog()|
+-----------------------+                   +-----------------------+
            |                                           |
            +---------------------+---------------------+
                                  |
                                  v
                  +--------------------------------+
                  |   Verdict Arbiter Agent        |
                  |   • Computes Calibrated P(Cheat)|
                  |   • Generates Explainable Proof|
                  +--------------------------------+
                                  |
                                  v
                  +--------------------------------+
                  | Final Disciplinary Enforcement |
                  +--------------------------------+
```

### Prompt & Tool Persona for the Verdict Arbiter Agent

```
ROLE: Senior Forensic Game Security Arbiter
OBJECTIVE:
Synthesize forensic analyses from the Kinematic Inspector Agent and Spatial Context Agent.
Determine whether the suspect player used third-party algorithmic assistance (aimbot, triggerbot, wallhack).

EVALUATION CRITERIA:
1. Physical Impossibility: Was the aim flick biologically achievable (Minimum Jerk satisfied)?
2. Sensory Plausibility: Did audio, radar, or prior engagement explain the crosshair pre-placement?
3. Reporter Reliability: Are reporting signals consistent with verified anomalous behavior?

CONFIDENCE CALCULATION:
- Assign a confidence rating between 0.00 and 1.00.
- Any score > 0.90 requires BOTH Kinematic and Spatial consensus.
- Provide a concise 3-sentence justification and the exact timestamps of anomalous ticks.
```
