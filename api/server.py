from __future__ import annotations

from typing import List

from fastapi import FastAPI

from logging_utils import setup_logging, logger
from retrieval.vector_store import SimpleVectorStore
from eligibility.rules import AtomicRule, Comparison, EligibilityRuleSet
from eligibility.engine import EligibilityEngine
from .models import QueryRequest, QueryResponse, SchemeEligibilityResult, EvidenceChunk


app = FastAPI(title="RAG-GOV Eligibility API")

# Module-level singletons initialised on startup
VECTOR_STORE: SimpleVectorStore | None = None
ENGINE: EligibilityEngine | None = None


@app.on_event("startup")
def startup_event() -> None:
    setup_logging()
    logger.info("Starting RAG-GOV API\n")
    # For now, build a very small demo ruleset with a single toy scheme.
    global VECTOR_STORE, ENGINE
    VECTOR_STORE = SimpleVectorStore()
    try:
        VECTOR_STORE.load_chunks()
        VECTOR_STORE.build_index()
    except FileNotFoundError:
        logger.warning("No chunks.jsonl found; retrieval will be empty.\n")

    demo_rules = EligibilityRuleSet(
        scheme_id="SCHEME_DEMO",
        rules=[
            AtomicRule(field="age", op=Comparison.GTE, value=18, description="Age must be at least 18."),
            AtomicRule(field="income", op=Comparison.LTE, value=250000, description="Income at most 2.5L."),
        ],
        provenance={"doc_id": "demo_doc", "section": "eligibility"},
    )
    ENGINE = EligibilityEngine([demo_rules])


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    if ENGINE is None:
        raise RuntimeError("Eligibility engine not initialised.")
    profile_dict = request.profile.dict()
    eligibility_results = ENGINE.evaluate_profile(profile_dict)

    # Simple retrieval ignoring scheme for now; students can later restrict by scheme metadata.
    evidence_raw: List[EvidenceChunk] = []
    if VECTOR_STORE is not None and request.question.strip():
        try:
            hits = VECTOR_STORE.search(request.question, k=request.top_k)
            for h in hits:
                evidence_raw.append(
                    EvidenceChunk(text=h["text"], score=h["score"], metadata=h["metadata"])
                )
        except Exception:
            evidence_raw = []

    results: List[SchemeEligibilityResult] = []
    for er in eligibility_results:
        label = er["label"]
        missing = er["missing_fields"]
        rule_texts = []
        for rres in er["results"]:
            r = rres["rule"]
            status = rres["value"]
            status_str = "unknown" if status is None else ("ok" if status else "fail")
            rule_texts.append(f"{r.description} [{status_str}]")
        explanation = " | ".join(rule_texts)
        results.append(
            SchemeEligibilityResult(
                scheme_id=er["scheme_id"],
                label=label,
                missing_fields=missing,
                explanation=explanation,
                evidence=evidence_raw,
            )
        )

    return QueryResponse(results=results)


