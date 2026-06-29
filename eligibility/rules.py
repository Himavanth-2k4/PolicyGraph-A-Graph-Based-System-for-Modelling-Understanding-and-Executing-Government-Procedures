from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Callable


class Comparison(str, Enum):
    LTE = "<="
    GTE = ">="
    EQ = "=="
    IN = "in"


@dataclass
class AtomicRule:
    """
    A simple atomic rule such as:
      profile.income <= 250000
      profile.age >= 18
      profile.category in ["SC", "ST"]
    """

    field: str
    op: Comparison
    value: Any
    description: str

    def evaluate(self, profile: Dict[str, Any]) -> bool | None:
        if self.field not in profile:
            return None  # unknown / missing
        v = profile[self.field]
        if self.op == Comparison.LTE:
            return v <= self.value
        if self.op == Comparison.GTE:
            return v >= self.value
        if self.op == Comparison.EQ:
            return v == self.value
        if self.op == Comparison.IN:
            return v in self.value
        return None


@dataclass
class EligibilityRuleSet:
    scheme_id: str
    rules: List[AtomicRule]
    provenance: Dict[str, Any]

    def evaluate(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        missing = []
        for r in self.rules:
            val = r.evaluate(profile)
            if val is None:
                missing.append(r.field)
            results.append({"rule": r, "value": val})

        if any(r["value"] is False for r in results):
            label = "NOT_ELIGIBLE"
        elif missing:
            label = "INSUFFICIENT_INFO"
        else:
            label = "ELIGIBLE"

        return {
            "scheme_id": self.scheme_id,
            "label": label,
            "results": results,
            "missing_fields": sorted(set(missing)),
            "provenance": self.provenance,
        }


__all__ = ["Comparison", "AtomicRule", "EligibilityRuleSet"]

