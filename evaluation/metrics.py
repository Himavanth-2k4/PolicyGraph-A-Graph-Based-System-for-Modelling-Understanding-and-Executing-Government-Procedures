from __future__ import annotations

from typing import List, Dict


def eligibility_accuracy(preds: List[Dict], gold: List[Dict]) -> float:
    """
    Compute simple accuracy over labels.
    Each dict must have keys: profile_id, scheme_id, label.
    """
    gold_map = {(g["profile_id"], g["scheme_id"]): g["label"] for g in gold}
    correct = 0
    total = 0
    for p in preds:
        key = (p["profile_id"], p["scheme_id"])
        if key not in gold_map:
            continue
        total += 1
        if p["label"] == gold_map[key]:
            correct += 1
    return correct / total if total else 0.0


__all__ = ["eligibility_accuracy"]

