from pathlib import Path

from dotenv import load_dotenv
from kaggle.api.kaggle_api_extended import KaggleApi


load_dotenv()


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


if __name__ == "__main__":
    dataset_path = download_dataset()
    print(dataset_path)