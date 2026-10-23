"""
Stage 3: Agentic Profile Inspector (Cheat Seller & Contact Intelligence)
========================================================================
Inspects player profile metadata (bio, custom status text, nickname, clan tag)
to detect commercial cheat sellers and external distribution handles.

Key Design Specifications:
  1. Obfuscation Resistance: Decodes homoglyphs, handles leetspeak substitutions,
     and strips zero-width spaces.
  2. Safety Invariant:
     - Outputs ONLY GREEN and GRAY.
     - A profile text string alone CANNOT prove in-game cheating and therefore
       NEVER directly brands a player RED.
  3. Contributes to Stage 4 Triangulation: When combined with suspicious DB stats
     and anomalous telemetry, flags from Stage 3 trigger the 3-GRAY promotion rule.
"""

from typing import List, Dict, Any, Optional
import re
import logging

logger = logging.getLogger("cds.agentic_profile")


class AgenticProfileInspector:
    """
    Profile intelligence engine detecting commercial cheat-seller language and contact links.
    """

    HOMOGLYPH_MAP = {
        "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x",
        "0": "o", "1": "i", "!": "i", "@": "a", "$": "s", "3": "e", "4": "a",
    }

    DEFAULT_SELLER_KEYWORDS = [
        r"\bcheats?\b", r"\bhacks?\b", r"\baimbots?\b", r"\besp\b", r"\bwallhacks?\b",
        r"\bmod\s*menu\b", r"\bscripts?\b", r"\bundetected\b", r"\bbypass\b",
        r"\bdma\b", r"\bvip\s*config\b", r"\bsell(ing)?\b", r"\bbuy\b",
        r"\bdm\s*for\b", r"\bcontact\b", r"\bcheap\b", r"\bdiscount\b", r"\bprice\b",
        r"\btrusted\b", r"\blifetime\b", r"\bslot(s)?\b", r"\bprivate\s*cheat\b"
    ]

    DEFAULT_CONTACT_PLATFORMS = [
        r"t\.me\/[a-zA-Z0-9_]+",
        r"telegram(?:\.me)?\/[a-zA-Z0-9_]+",
        r"\btelegrams?\b",
        r"discord(?:\.gg|\.com\/invite)\/[a-zA-Z0-9]+",
        r"\bdc\s*:\s*[a-zA-Z0-9_#]+",
        r"wa\.me\/[0-9]+",
        r"\bwhatsapps?\b",
        r"\binsta(gram)?\b",
        r"\bwechat\b",
        r"\bqq\s*:\s*[0-9]+",
    ]

    def __init__(
        self,
        custom_seller_keywords: Optional[List[str]] = None,
        custom_contact_patterns: Optional[List[str]] = None,
        gray_score_threshold: float = 0.40,
    ):
        """
        :param custom_seller_keywords: Additional game-specific cheat/seller regex strings.
        :param custom_contact_patterns: Additional social/communication platform regexes.
        :param gray_score_threshold: Suspicion score above which profile is marked GRAY.
        """
        self.seller_keywords = list(self.DEFAULT_SELLER_KEYWORDS)
        if custom_seller_keywords:
            self.seller_keywords.extend(custom_seller_keywords)

        self.contact_platforms = list(self.DEFAULT_CONTACT_PLATFORMS)
        if custom_contact_patterns:
            self.contact_platforms.extend(custom_contact_patterns)

        self.gray_score_threshold = gray_score_threshold

    def normalize_text(self, text: str) -> str:
        """
        Normalizes leetspeak, homoglyphs, and zero-width spaces for robust regex matching.
        """
        if not text:
            return ""
        # Remove zero-width spaces and control characters
        cleaned = re.sub(r"[\u200B-\u200D\uFEFF]", "", text.lower())
        # Replace homoglyphs
        normalized = "".join(self.HOMOGLYPH_MAP.get(ch, ch) for ch in cleaned)
        return normalized

    def inspect_text(self, text: str) -> Dict[str, Any]:
        """
        Evaluates a raw profile string.
        Returns suspicion score and classification tier (GREEN or GRAY only).
        """
        normalized = self.normalize_text(text)

        matched_keywords = [
            kw for kw in self.seller_keywords if re.search(kw, normalized)
        ]
        matched_contacts = [
            cp for cp in self.contact_platforms if re.search(cp, normalized)
        ]

        score = 0.0
        reasons = []

        # High confidence: seller keywords + external contact channel
        if matched_keywords and matched_contacts:
            score += 0.75
            reasons.append(
                f"Commercial seller intent with external contact platform: {matched_contacts[:2]}"
            )
        elif matched_keywords:
            score += min(0.50, len(matched_keywords) * 0.25)
            reasons.append(f"Cheat terminology in profile text: {matched_keywords[:3]}")
        elif matched_contacts:
            # Check for commercial keywords
            if any(term in normalized for term in ["vip", "shop", "service", "store", "config", "buy"]):
                score += 0.45
                reasons.append(f"Commercial contact channel in profile: {matched_contacts[:2]}")
            else:
                score += 0.15

        score = min(1.0, score)
        # Safety Invariant: Tier is strictly GREEN or GRAY (NEVER RED)
        tier = "GRAY" if score >= self.gray_score_threshold else "GREEN"

        return {
            "tier": tier,
            "suspicion_score": round(score, 3),
            "reasons": reasons,
            "matched_keywords": matched_keywords,
            "matched_contacts": matched_contacts,
        }

    def inspect_profiles(
        self,
        profiles: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluates a batch of player profile records.
        Each record should contain 'player_id' and text fields like 'bio', 'nickname', 'clan_tag'.
        """
        rosters: Dict[str, List[str]] = {"GREEN": [], "GRAY": []}
        details: List[Dict[str, Any]] = []

        for p in profiles:
            pid = str(p.get("player_id", "unknown"))
            bio = str(p.get("bio", ""))
            nickname = str(p.get("nickname", ""))
            clan_tag = str(p.get("clan_tag", ""))
            combined_text = f"{nickname} {clan_tag} {bio}"

            res = self.inspect_text(combined_text)
            tier = res["tier"]
            rosters[tier].append(pid)
            details.append({
                "player_id": pid,
                "tier": tier,
                "suspicion_score": res["suspicion_score"],
                "reasons": res["reasons"],
            })

        return {
            "rosters": rosters,
            "details": details,
            "total_evaluated": len(profiles),
        }
