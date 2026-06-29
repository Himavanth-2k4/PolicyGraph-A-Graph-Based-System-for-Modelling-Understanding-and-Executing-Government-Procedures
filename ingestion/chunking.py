from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict

from .parsers import Section


@dataclass
class Chunk:
    doc_id: str
    chunk_id: str
    text: str
    metadata: Dict


def simple_sentence_chunk(section: Section, max_chars: int = 800) -> List[Chunk]:
    """
    Naive chunker: split by sentences and group up to max_chars.
    """
    text = section.text.replace("\n", " ")
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    chunks: List[Chunk] = []
    buf: List[str] = []
    current_len = 0
    counter = 0
    for sent in sentences:
        if current_len + len(sent) > max_chars and buf:
            counter += 1
            chunk_text = ". ".join(buf) + "."
            chunks.append(
                Chunk(
                    doc_id=section.doc_id,
                    chunk_id=f"{section.section_id}_c{counter}",
                    text=chunk_text,
                    metadata={"page": section.page, "section_id": section.section_id},
                )
            )
            buf = []
            current_len = 0
        buf.append(sent)
        current_len += len(sent) + 2

    if buf:
        counter += 1
        chunk_text = ". ".join(buf) + "."
        chunks.append(
            Chunk(
                doc_id=section.doc_id,
                chunk_id=f"{section.section_id}_c{counter}",
                text=chunk_text,
                metadata={"page": section.page, "section_id": section.section_id},
            )
        )
    return chunks


__all__ = ["Chunk", "simple_sentence_chunk"]

