from __future__ import annotations

from typing import Dict, List, Any

from .rules import EligibilityRuleSet


class EligibilityEngine:
    """
    Very small orchestrator for evaluating multiple schemes for a profile.
    """

    def __init__(self, rulesets: List[EligibilityRuleSet]):
        self.rulesets = rulesets

    def evaluate_profile(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [rs.evaluate(profile) for rs in self.rulesets]


__all__ = ["EligibilityEngine"]

