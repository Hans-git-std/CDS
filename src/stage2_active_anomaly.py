"""
Stage 2: Active Detector (Real-Time Kinematic & Gameplay Anomaly Detection)
Processes live in-game telemetry streams (movement speed, height/elevation,
damage per minute, active KD, micro-aim adjustments).
Discards GREEN (nominal players) and reports only GRAY and RED.
"""

from typing import Dict, Any, Optional, List


class ActiveAnomalyDetector:
    def __init__(
        self,
        max_legitimate_speed: float = 16.0,  # Max sprint speed m/s
        max_legitimate_height: float = 60.0, # Max elevation jump/climb delta m
        max_legitimate_dpm: float = 1800.0,  # Max human damage per minute
    ):
        self.max_legitimate_speed = max_legitimate_speed
        self.max_legitimate_height = max_legitimate_height
        self.max_legitimate_dpm = max_legitimate_dpm

    def evaluate_tick(self, telemetry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluates a real-time telemetry tick from an active battleground match.
        Filters out clean players (GREEN) and returns alerts ONLY for GRAY or RED.
        """
        player_id = telemetry.get("player_id", "UNKNOWN")
        speed = telemetry.get("movement_speed", 0.0)
        height = telemetry.get("player_height", 0.0)
        active_dpm = telemetry.get("active_dpm", 0.0)
        active_kd = telemetry.get("active_kd", 1.0)
        active_hs = telemetry.get("active_headshot_rate", 0.15)
        micro_aim_snap = telemetry.get("micro_aim_snap", False)

        anomaly_points = 0
        reasons = []

        # 1. Physical Speed Violation (Speed hack)
        if speed > self.max_legitimate_speed * 1.8:
            anomaly_points += 50
            reasons.append(f"CRITICAL_SPEED_EXPLOIT: {speed:.1f} m/s")
        elif speed > self.max_legitimate_speed * 1.2:
            anomaly_points += 20
            reasons.append(f"ELEVATED_SPEED: {speed:.1f} m/s")

        # 2. Elevation / Fly Hack Violation
        if height > self.max_legitimate_height * 2.0:
            anomaly_points += 50
            reasons.append(f"CRITICAL_FLY_EXPLOIT: height {height:.1f}m")
        elif height > self.max_legitimate_height:
            anomaly_points += 20
            reasons.append(f"SUSPICIOUS_ELEVATION: {height:.1f}m")

        # 3. Combat DPS & Headshot Acceleration
        if active_dpm > self.max_legitimate_dpm * 1.5 and active_hs > 0.80:
            anomaly_points += 35
            reasons.append(f"COMBAT_OVERLOAD: DPM={active_dpm:.0f}, HS={active_hs*100:.1f}%")
        elif active_dpm > self.max_legitimate_dpm or active_hs > 0.65:
            anomaly_points += 15
            reasons.append("HIGH_COMBAT_BURST")

        # 4. Micro-aim Snap
        if micro_aim_snap:
            anomaly_points += 25
            reasons.append("NON_BIOLOGICAL_MICRO_AIM_SNAP")

        # Tier Decision
        if anomaly_points >= 50:
            tier = "RED"
        elif anomaly_points >= 20:
            tier = "GRAY"
        else:
            # Clean player: discard immediately (do not store or alert)
            return None

        return {
            "player_id": player_id,
            "tier": tier,
            "anomaly_points": anomaly_points,
            "reasons": reasons,
            "tick_telemetry": telemetry
        }

    def process_telemetry_batch(self, telemetry_records: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Processes real-time telemetry events and partitions active suspects into GRAY and RED.
        GREEN players are cleared / omitted.
        """
        results = {"GRAY": [], "RED": []}
        for telem in telemetry_records:
            eval_res = self.evaluate_tick(telem)
            if eval_res is not None:
                tier = eval_res["tier"]
                results[tier].append(eval_res["player_id"])
        return results
