# 📐 CDS Technical Architecture & Systems Engineering

This document specifies the internal engineering, TensorFlow neural network architectures, anomaly reconstruction equations, and consensus mechanics of the **Cheat Detection System (CDS)**.

---

## 1. System Topology & Processing Tiers

```
+---------------------------------------------------------------------------------------------------+
|                                 DEVELOPER INTEGRATION BOUNDARIES                                  |
|                                                                                                   |
|    +----------------------------------+             +----------------------------------------+    |
|    | Game Database (Historical Stats) |             | Game Server Telemetry (Live Stream)    |    |
|    | Features chosen by DEVELOPER     |             | Features chosen by DEVELOPER           |    |
|    +----------------------------------+             +----------------------------------------+    |
|                     |                                                   |                         |
|                     v                                                   v                         |
|    +----------------------------------+             +----------------------------------------+    |
|    | STAGE 1: PASSIVE NLP DETECTOR    |             | STAGE 2: ACTIVE ANOMALY DETECTOR       |    |
|    | • TensorFlow Sequential Model    |             | • TensorFlow Sequential Autoencoder    |    |
|    | • Trained on Answer Key (0 & 1)  |             | • Trained on normal telemetry          |    |
|    | • Outputs: GREEN, GRAY, RED      |             | • Drops GREEN early -> GRAY, RED       |    |
|    +----------------------------------+             +----------------------------------------+    |
|                     |                                                   |                         |
|                     +---------------------+       +---------------------+                         |
|                                           |       |                                               |
|                                           v       v                                               |
|    +----------------------------------+   +--------------------------------------------------+    |
|    | Player Profiles & Social Metadata|   | STAGE 4: CENTRAL PIPELINE ORCHESTRATOR           |    |
|    | (Bio, Nickname, Clan Tags)       |   | • Balances simultaneous execution                |    |
|    +----------------------------------+   | • Aggregates and cross-routes GRAY lists         |    |
|                     |                     | • 3-GRAY Promotion Rule: 3x GRAY ===> RED!       |    |
|                     v                     | • 2-GRAY Retention Rule: 2x GRAY ===> Keep GRAY  |    |
|    +----------------------------------+   +--------------------------------------------------+    |
|    | STAGE 3: AGENTIC PROFILE AGENT   |                             |                             |
|    | • Scans for cheat sellers (DC/TG)|                             v                             |
|    | • Outputs: GREEN / GRAY only     |   +--------------------------------------------------+    |
|    +----------------------------------+   | FINAL CLASSIFIED ROSTERS: [ GREEN | GRAY | RED ] |    |
|                     |                     | Developer Handover: Free | Monitor | Ban         |    |
|                     +-------------------->+--------------------------------------------------+    |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Component Engineering & TensorFlow Specifications

### 2.0 Feature Preprocessing & Scaling (`FeatureScaler`)
Anti-cheat datasets exhibit heterogeneous distributions (e.g. win rates $\in [0, 1]$, K/D ratios $\in [0, 50]$, DPM $\in [0, 4000]$).
CDS provides an embedded `FeatureScaler` supporting:
* **MinMax Normalization:** $x_{\text{scaled}} = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$ (Used by Stage 1).
* **Z-Score Standardization:** $z = \frac{x - \mu}{\sigma}$ (Used by Stage 2 to prevent clamping extreme kinematic telemetry anomalies).
* **Missing Value Imputation:** Column-median substitution for packet drops or null values.

---

### 2.1 Stage 1: Passive Detector (TensorFlow Sequential)
Stage 1 accepts an arbitrary numerical feature matrix $X \in \mathbb{R}^{N \times D}$ representing historical player stats extracted from the game database.

#### Architecture:
```python
tf.keras.Sequential([
    tf.keras.layers.Input(shape=(input_dim,)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')  # Continuous risk score [0, 1]
])
```

#### Loss & Optimizer:
* **Loss Function:** Binary Cross-Entropy
  $$\mathcal{L} = -\frac{1}{N} \sum_{i=1}^N \left( y_i \log(\hat{y}_i) + (1 - y_i)\log(1 - \hat{y}_i) \right)$$
* **Optimizer:** Adam ($\alpha = 0.01$)

#### Training Mode vs. Inference Partitioning:
* **Training Mode:** The developer supplies a ground-truth Answer Key where labels are binary:
  $$y_i \in \{0, 1\} \quad (0 = \text{GREEN}, \ 1 = \text{RED})$$
  *(Ground-truth training contains NO mid-tier GRAY).*
* **Inference Partitioning:**
  $$\text{Tier}_{S1}(x) = \begin{cases} \text{GREEN} & \text{if } \hat{y} < 0.35 \\ \text{GRAY} & \text{if } 0.35 \le \hat{y} < 0.75 \\ \text{RED} & \text{if } \hat{y} \ge 0.75 \end{cases}$$

---

### 2.2 Stage 2: Active Anomaly Detector (TensorFlow Sequential Autoencoder)
Stage 2 accepts streaming real-time telemetry vectors $X_{\text{telem}} \in \mathbb{R}^{N \times K}$ from active matches.

#### Architecture:
```python
tf.keras.Sequential([
    # Input
    tf.keras.layers.Input(shape=(input_dim,)),
    # Encoder
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(8, activation='relu'),   # Latent bottleneck
    # Decoder
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(input_dim, activation='linear') # Reconstruction
])
```

#### Anomaly Reconstruction Error:
Given an input vector $x$ and its autoencoder reconstruction $\hat{x}$, the Mean Squared Error (MSE) is:

$$\text{MSE}(x, \hat{x}) = \frac{1}{K} \sum_{j=1}^K (x_j - \hat{x}_j)^2$$

#### Alerting Behavior:
* **GREEN:** $\text{MSE} < 0.08$ $\rightarrow$ **Removed / Discarded immediately** (omitted from reporting to conserve server memory and CPU).
* **GRAY:** $0.08 \le \text{MSE} < 0.25$ $\rightarrow$ Reported as suspicious telemetry.
* **RED:** $\text{MSE} \ge 0.25$ $\rightarrow$ Reported as critical kinematic exploit.

---

### 2.3 Stage 3: Agentic Profile Inspector (Seller Intelligence)
Analyzes user metadata (profile bio text, custom nicknames, clan tags) to detect commercial cheat distributors advertising on external channels (Discord, Telegram, WhatsApp).

#### Safety Invariant:
$$\text{Output}_{S3} \in \{\text{GREEN}, \text{GRAY}\}$$
*(Stage 3 never outputs RED on profile text alone).*

---

### 2.4 Stage 4: Central Pipeline Orchestrator & Consensus Engine

Stage 4 runs all models simultaneously and merges their output rosters:

Let $S_1(p), S_2(p), S_3(p)$ be the tier classifications for player $p$.

#### Consensus Formulation:
1. **Direct RED Rule:**
   $$\text{FinalTier}(p) = \text{RED} \quad \text{if } S_1(p) = \text{RED} \lor S_2(p) = \text{RED}$$

2. **The 3-GRAY Promotion Rule:**
   $$\text{FinalTier}(p) = \text{RED} \quad \text{if } S_1(p) = \text{GRAY} \land S_2(p) = \text{GRAY} \land S_3(p) = \text{GRAY}$$

3. **The 2-GRAY Retention Rule:**
   $$\text{FinalTier}(p) = \text{GRAY} \quad \text{if } \sum_{i=1}^3 \mathbb{I}(S_i(p) = \text{GRAY}) \in \{1, 2\} \land \text{FinalTier}(p) \ne \text{RED}$$

4. **Nominal Baseline Rule:**
   $$\text{FinalTier}(p) = \text{GREEN} \quad \text{otherwise}$$

---

## 3. Developer Handover & Action Handshake

CDS returns clean rosters ready for game backend execution:

```json
{
  "summary": {
    "total_players": 100,
    "green_count": 94,
    "gray_count": 4,
    "red_count": 2
  },
  "rosters": {
    "GREEN": ["P1", "P2", "..."],
    "GRAY": ["P3", "P4", "..."],
    "RED": ["P5", "P6"]
  },
  "developer_handover": {
    "GREEN": "Free / Allow normal play.",
    "GRAY": "Monitor / Increase tick sampling rate, record demo, soft trust queue.",
    "RED": "Ban or Quarantine / Disconnect, HWID ban, or route to shadow-lobbies."
  }
}
```
