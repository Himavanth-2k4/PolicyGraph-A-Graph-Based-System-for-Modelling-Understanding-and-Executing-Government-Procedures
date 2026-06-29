from __future__ import annotations

from typing import List, Dict, Any


def demo_profiles() -> List[Dict[str, Any]]:
    """
    Very small set of synthetic profiles for quick manual testing.
    """
    return [
        {"id": "p1", "age": 19, "income": 150000, "category": "SC", "student": True},
        {"id": "p2", "age": 30, "income": 400000, "category": "OBC", "student": False},
    ]


__all__ = ["demo_profiles"]

