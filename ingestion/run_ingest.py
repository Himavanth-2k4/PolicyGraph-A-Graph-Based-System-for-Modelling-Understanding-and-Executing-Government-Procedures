import json
import sys
from pathlib import Path

# Make project root importable when running as a script:
#   python ingestion/run_ingest.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import config
from logging_utils import setup_logging, logger
from ingestion.loaders import list_raw_documents, build_doc_metadata
from ingestion.parsers import parse_document
from ingestion.chunking import simple_sentence_chunk


def main() -> None:
    setup_logging()
    out_dir = config.paths.data_processed
    out_dir.mkdir(parents=True, exist_ok=True)

    docs = list_raw_documents()
    all_chunks = []

    for path in docs:
        meta = build_doc_metadata(path)
        sections = parse_document(path, meta)
        for section in sections:
            chunks = simple_sentence_chunk(section)
            for ch in chunks:
                all_chunks.append(
                    {
                        "doc_id": ch.doc_id,
                        "chunk_id": ch.chunk_id,
                        "text": ch.text,
                        "metadata": ch.metadata | {"filename": meta["filename"]},
                    }
                )

    out_path = out_dir / "chunks.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for row in all_chunks:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    logger.info(f"Wrote {len(all_chunks)} chunks to {out_path}\n")


if __name__ == "__main__":
    main()

