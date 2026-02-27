import os
from dotenv import load_dotenv


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")
_raw_dimensions = os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "1536")
try:
    OPENAI_EMBEDDING_DIMENSIONS = int(_raw_dimensions)
except ValueError:
    raise ValueError(
        f"OPENAI_EMBEDDING_DIMENSIONS must be an integer, got: '{_raw_dimensions}'"
    )
OPENAI_EMBEDDING_LIMIT = int(os.getenv("OPENAI_EMBEDDING_LIMIT", "8192"))