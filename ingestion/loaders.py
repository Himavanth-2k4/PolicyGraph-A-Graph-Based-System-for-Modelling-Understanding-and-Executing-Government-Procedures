from pathlib import Path
from typing import Iterable, List, Dict

from config import config
from logging_utils import logger


def list_raw_documents(extensions: Iterable[str] = (".pdf", ".html", ".htm")) -> List[Path]:
    """
    List raw documents in data/raw with the given extensions.
    """
    raw_dir = config.paths.data_raw
    raw_dir.mkdir(parents=True, exist_ok=True)
    exts = {e.lower() for e in extensions}
    docs: List[Path] = []
    for p in raw_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            docs.append(p)
    logger.info(f"Found {len(docs)} raw documents in {raw_dir}\n")
    return docs


def build_doc_metadata(path: Path) -> Dict:
    """
    Minimal metadata builder; students can extend this later.
    """
    return {
        "doc_id": path.stem,
        "filename": path.name,
        "source_path": str(path),
        "jurisdiction": None,
        "department": None,
        "language": None,
    }


__all__ = ["list_raw_documents", "build_doc_metadata"]

