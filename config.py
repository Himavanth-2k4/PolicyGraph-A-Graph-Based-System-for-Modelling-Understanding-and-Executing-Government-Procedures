from pathlib import Path
from pydantic import BaseModel


class Paths(BaseModel):
    # config.py now lives at the project root, so .parent is the project dir
    project_root: Path = Path(__file__).resolve().parent
    data_raw: Path = project_root / "data" / "raw"
    data_processed: Path = project_root / "data" / "processed"
    data_indices: Path = project_root / "data" / "indices"


class EmbeddingConfig(BaseModel):
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    batch_size: int = 16


class AppConfig(BaseModel):
    paths: Paths = Paths()
    embeddings: EmbeddingConfig = EmbeddingConfig()


config = AppConfig()

