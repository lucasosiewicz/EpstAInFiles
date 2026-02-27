import tiktoken
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from patterns.singleton import Singleton
from utils import OPENAI_API_KEY, OPENAI_EMBEDDING_DIMENSIONS, OPENAI_EMBEDDING_LIMIT, OPENAI_EMBEDDING_MODEL


class EmbeddingModel(Singleton):
    def __init__(self):
        if hasattr(self, "embeddings"):
            return
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        if not OPENAI_EMBEDDING_MODEL:
            raise ValueError("OPENAI_EMBEDDING_MODEL environment variable is not set.")
        self.embeddings = OpenAIEmbeddings(
            model=OPENAI_EMBEDDING_MODEL,
            api_key=OPENAI_API_KEY,
            dimensions=OPENAI_EMBEDDING_DIMENSIONS,
            request_timeout=10.0,
            skip_empty=True,
            max_retries=3,
            retry_min_seconds=1,
        )
        self.embeddings.validate_environment()
        self._tokenizer = tiktoken.get_encoding("cl100k_base")
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=OPENAI_EMBEDDING_LIMIT,
            chunk_overlap=50,
            length_function=lambda text: len(self._tokenizer.encode(text)),
        )

    def _chunk(self, text: str) -> list[str]:
        tokens = self._tokenizer.encode(text)
        if len(tokens) <= OPENAI_EMBEDDING_LIMIT:
            return [text]
        return self._text_splitter.split_text(text)

    def embed_documents(self, documents: list[str]) -> list[list[float]]:
        chunks = [c for doc in documents for c in self._chunk(doc)]
        return self.embeddings.embed_documents(chunks)

    def embed_query(self, query: str) -> list[list[float]]:
        chunks = self._chunk(query)
        return [self.embeddings.embed_query(chunk) for chunk in chunks]
