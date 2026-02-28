from pathlib import Path
import json
from typing import Iterator

from kaggle.api.kaggle_api_extended import KaggleApi
from sqlalchemy.orm import Session


def download_dataset(
    dataset_name: str = "linogova/epstein-ranker-dataset-u-s-house-oversight",
    path: str = "data",
) -> Path:
    output_dir = Path(path)
    output_dir.mkdir(parents=True, exist_ok=True)
    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(dataset_name, path=str(output_dir), unzip=True)
    return output_dir

def get_dataset_files(path: Path) -> Iterator[Path]:
    return path.glob("*.jsonl")

def load_dataset_file_as_jsons(filepath: Path) -> Iterator[dict]:
    with open(filepath, "r") as f:
        rows = f.readlines()
        for row in rows:
            yield json.loads(row)

def get_or_create(session: Session, model: type, name: str):
    instance = session.query(model).filter(model.name == name).first()
    if not instance:
        instance = model(name=name)
        session.add(instance)
        session.flush()
    return instance

def build_document_text(data: dict) -> str:
    parts = [
        data.get("headline", ""),
        data.get("reason", ""),
        "\n".join(data.get("key_insights", []) or []),
    ]
    meta = data.get("metadata") or {}
    if isinstance(meta, dict) and meta.get("text"):
        parts.append(meta["text"])
    return "\n\n".join(p for p in parts if p)
