from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

import fitz  # pymupdf

from logging_utils import logger


@dataclass
class Section:
    doc_id: str
    section_id: str
    title: str | None
    text: str
    page: int | None = None


def parse_pdf(path: Path, doc_id: str) -> List[Section]:
    """
    Very simple PDF parser using PyMuPDF.
    Splits by page; later students can add heading detection.
    """
    logger.info(f"Parsing PDF: {path}\n")
    sections: List[Section] = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc):
            text = page.get_text("text")
            if not text.strip():
                continue
            section_id = f"{doc_id}_p{i+1}"
            sections.append(Section(doc_id=doc_id, section_id=section_id, title=None, text=text, page=i + 1))
    return sections


def parse_document(path: Path, metadata: Dict) -> List[Section]:
    suffix = path.suffix.lower()
    doc_id = metadata.get("doc_id", path.stem)
    if suffix == ".pdf":
        return parse_pdf(path, doc_id=doc_id)
    # For HTML/others, a stub to be extended:
    logger.warning(f"No specific parser implemented for {suffix}, skipping: {path}\n")
    return []


__all__ = ["Section", "parse_document"]

