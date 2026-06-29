from __future__ import annotations

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    income: Optional[float] = None
    category: Optional[str] = Field(None, description="e.g. SC, ST, OBC, General")
    state: Optional[str] = None
    district: Optional[str] = None
    occupation: Optional[str] = None
    disability: Optional[bool] = None
    student: Optional[bool] = None


class QueryRequest(BaseModel):
    profile: UserProfile
    question: str
    top_k: int = 5


class EvidenceChunk(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any]


class SchemeEligibilityResult(BaseModel):
    scheme_id: str
    label: str
    missing_fields: List[str]
    explanation: str
    evidence: List[EvidenceChunk]


class QueryResponse(BaseModel):
    results: List[SchemeEligibilityResult]


__all__ = ["UserProfile", "QueryRequest", "QueryResponse", "SchemeEligibilityResult", "EvidenceChunk"]

