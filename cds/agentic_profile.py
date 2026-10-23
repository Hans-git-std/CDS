"""
Stage 3: Agentic Profile Inspector (Cheat Seller & Contact Intelligence)
------------------------------------------------------------------------
Pulls player profile metadata from the database (bio, nickname, clan tag,
custom status text, contact handles).
Evaluates whether players are suspicious cheat sellers (e.g. promoting Discord,
Telegram, WhatsApp, hack formulas, or cheat configs).
Safety Invariant:
  - Outputs ONLY GREEN and GRAY.
  - We cannot definitively tell a player is RED solely on the basis of their profile text.
"""

from typing import List, Dict, Any, Optional
import re


class AgenticProfileInspector:
    def __init__(self, custom_seller_keywords: Optional[List[str]] = None):
        """
        Initializes the Agentic Profile Inspector.
        Developers can optionally supply game-specific seller keywords.
        """
        base_keywords = [
            r"\bcheats?\b", r"\bhacks?\b", r"\baimbots?\b", r"\besp\b", r"\bwallhacks?\b",
            r"\bmod\s*menu\b", r"\bscripts?\b", r"\bundetected\b", r"\bbypass\b",
            r"\bdma\b", r"\bvip\s*config\b", r"\bsell(ing)?\b", r"\bbuy\b",
            r"\bdm\s*for\b", r"\bcontact\b", r"\bcheap\b", r"\bdiscount\b"
        ]
        if custom_seller_keywords:
            base_keywords.extend(custom_seller_keywords)
        self.seller_keywords = base_keywords

        self.contact_platforms = [
            r"t\.me\/", r"\btelegrams?\b", r"discord(\.gg)?", r"\bdc\s*:\s*\w+",
            r"\bwhatsapps?\b", r"wa\.me\/", r"\binsta(gram)?\b", r"\bwechat\b", r"\bqq\s*:\s*\w+"
        ]

    def inspect_text(self, text: str) -> Dict[str, Any]:
        """
        Evaluates profile text strings for cheat-seller markers and contact handles.
        """
        lower_text = text.lower()
        matched_keywords = [kw for kw in self.seller_keywords if re.search(kw, lower_text)]
        matched_contacts = [cp for cp in self.contact_platforms if re.search(cp, lower_text)]

        is_suspicious = False
        reasons = []

        # Cheat keywords combined with contact platforms indicate high seller probability
        if matched_keywords and matched_contacts:
            is_suspicious = True
            reasons.append(f"Cheat seller keywords with contact handle: {matched_keywords[:2]}, {matched_contacts[:2]}")
        elif matched_keywords:
            is_suspicious = True
            reasons.append(f"Cheat terminology detected: {matched_keywords[:3]}")
        elif matched_contacts and any(term in lower_text for term in ["vip", "shop", "service", "config"]):
            is_suspicious = True
            reasons.append("Commercial contact handle in profile status")

        tier = "GRAY" if is_suspicious else "GREEN"
        return {
            "tier": tier,
            "reasons": reasons,
        }

    def inspect_profiles(
        self,
        profiles: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluates a batch of player profile records.
        Returns rosters: GREEN and GRAY only.
        """
        rosters = {"GREEN": [], "GRAY": []}
        details = []

        for p in profiles:
            pid = p.get("player_id", "unknown")
            bio = p.get("bio", "")
            nickname = p.get("nickname", "")
            clan_tag = p.get("clan_tag", "")
            combined_text = f"{nickname} {clan_tag} {bio}"

            res = self.inspect_text(combined_text)
            tier = res["tier"]
            rosters[tier].append(pid)
            details.append({
                "player_id": pid,
                "tier": tier,
                "reasons": res["reasons"],
            })

        return {
            "rosters": rosters,
            "details": details,
        }
