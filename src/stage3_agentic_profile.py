"""
Stage 3: Agentic Profile Inspector (Cheat Seller & Contact Intelligence)
Many cheat users advertise/sell their hack scripts, configs, or formulas by
placing contact info (Discord, Telegram, WhatsApp, URLs) in their profile/ID.
This stage uses LLM agentic heuristics to inspect user profile data.
Safety Rule: Outputs ONLY GREEN and GRAY (never RED directly from profile text).
"""

from typing import Dict, Any, List
import re


class AgenticProfileInspector:
    def __init__(self):
        # Known cheat seller triggers and communication platforms
        self.seller_keywords = [
            r"cheat", r"hack", r"aimbot", r"esp", r"wallhack", r"mod\s*menu",
            r"script", r"undetected", r"bypass", r"dma", r"vip\s*config",
            r"sell", r"buy", r"dm\s*for", r"contact", r"cheap", r"discount"
        ]
        self.contact_platforms = [
            r"t\.me\/", r"telegram", r"discord(\.gg)?", r"dc:", r"whatsapp",
            r"wa\.me", r"insta", r"wechat", r"qq:"
        ]

    def inspect_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Inspects profile metadata: nickname, bio status, clan tag, and external handles.
        Outputs ONLY 'GREEN' or 'GRAY' (A profile alone cannot be definitively RED).
        """
        player_id = profile_data.get("player_id", "UNKNOWN")
        nickname = profile_data.get("nickname", "").lower()
        bio = profile_data.get("bio", "").lower()
        clan_tag = profile_data.get("clan_tag", "").lower()
        full_text = f"{nickname} {clan_tag} {bio}"

        has_seller_keyword = any(re.search(kw, full_text) for kw in self.seller_keywords)
        has_contact_platform = any(re.search(cp, full_text) for cp in self.contact_platforms)

        suspicious_flags = []
        if has_seller_keyword and has_contact_platform:
            suspicious_flags.append("HIGH_CONFIDENCE_CHEAT_SELLER_PROFILE")
        elif has_seller_keyword:
            suspicious_flags.append("SUSPICIOUS_CHEAT_TERMINOLOGY_IN_BIO")
        elif has_contact_platform and ("vip" in full_text or "shop" in full_text):
            suspicious_flags.append("PROBABLE_UNOFFICIAL_COMMERCIAL_HANDLE")

        # Decision: GREEN or GRAY
        if len(suspicious_flags) > 0:
            tier = "GRAY"
        else:
            tier = "GREEN"

        return {
            "player_id": player_id,
            "tier": tier,
            "suspicious_flags": suspicious_flags,
            "agent_analysis": (
                "Profile contains commercial/seller markers or contact handles."
                if tier == "GRAY" else "Profile text is nominal and clear of seller patterns."
            )
        }

    def inspect_batch(self, profiles: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Processes a batch of player profiles and returns GREEN and GRAY rosters.
        """
        results = {"GREEN": [], "GRAY": []}
        for prof in profiles:
            eval_res = self.inspect_profile(prof)
            tier = eval_res["tier"]
            results[tier].append(eval_res["player_id"])
        return results
