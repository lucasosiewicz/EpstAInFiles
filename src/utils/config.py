import os
from dotenv import load_dotenv


load_dotenv()


def get_env(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if not value:
        raise ValueError(f"Environment variable {key} is not set")
    return value


OPENAI_API_KEY = get_env("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = get_env("OPENAI_EMBEDDING_MODEL")
OPENAI_EMBEDDING_DIMENSIONS = int(get_env("OPENAI_EMBEDDING_DIMENSIONS", "1536"))
OPENAI_EMBEDDING_LIMIT = int(get_env("OPENAI_EMBEDDING_LIMIT", "8192"))
DATABASE_URL = get_env("DATABASE_URL", "postgresql+psycopg://epstain:epstain@localhost:5432/epstainfiles")