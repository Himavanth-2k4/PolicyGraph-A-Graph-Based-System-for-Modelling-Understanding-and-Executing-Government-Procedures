from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from sentence_transformers import SentenceTransformer

from config import config
from logging_utils import logger


@dataclass
class VectorRecord:
    doc_id: str
    chunk_id: str
    text: str
    metadata: Dict[str, Any]


class SimpleVectorStore:
    """
    Minimal in-memory vector store backed by numpy arrays.
    Good enough for a student-scale prototype.
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or config.embeddings.model_name
        self.model = SentenceTransformer(self.model_name)
        self.records: List[VectorRecord] = []
        self.embeddings: np.ndarray | None = None

    def load_chunks(self, chunks_file: Path | None = None) -> None:
        chunks_file = chunks_file or (config.paths.data_processed / "chunks.jsonl")
        if not chunks_file.exists():
            raise FileNotFoundError(f"Chunks file not found: {chunks_file}")
        logger.info(f"Loading chunks from {chunks_file}\n")
        self.records.clear()
        with chunks_file.open("r", encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                self.records.append(
                    VectorRecord(
                        doc_id=row["doc_id"],
                        chunk_id=row["chunk_id"],
                        text=row["text"],
                        metadata=row.get("metadata", {}),
                    )
                )

    def build_index(self, batch_size: int | None = None) -> None:
        batch_size = batch_size or config.embeddings.batch_size
        texts = [r.text for r in self.records]
        logger.info(f"Encoding {len(texts)} chunks with model={self.model_name}\n")
        embs = self.model.encode(texts, batch_size=batch_size, show_progress_bar=True, convert_to_numpy=True)
        self.embeddings = embs.astype("float32")

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if self.embeddings is None:
            raise RuntimeError("Embeddings index not built.")
        q = self.model.encode([query], convert_to_numpy=True).astype("float32")[0]
        q_norm = q / (np.linalg.norm(q) + 1e-8)
        doc_norms = self.embeddings / (np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-8)
        scores = doc_norms @ q_norm
        top_idx = np.argsort(-scores)[:k]
        results: List[Dict[str, Any]] = []
        for idx in top_idx:
            rec = self.records[int(idx)]
            results.append(
                {
                    "score": float(scores[int(idx)]),
                    "doc_id": rec.doc_id,
                    "chunk_id": rec.chunk_id,
                    "text": rec.text,
                    "metadata": rec.metadata,
                }
            )
        return results


__all__ = ["SimpleVectorStore", "VectorRecord"]

