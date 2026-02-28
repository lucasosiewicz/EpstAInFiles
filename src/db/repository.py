from sqlalchemy.orm import Session

from db.models import (
    Agency,
    Document,
    DocumentChunk,
    DocumentKeyInsight,
    LeadType,
    PowerMention,
    Tag,
)
from utils import get_or_create


LOOKUPS = (
    ("tags", Tag, "tags"),
    ("power_mentions", PowerMention, "power_mentions"),
    ("agency_involvement", Agency, "agencies"),
    ("lead_types", LeadType, "lead_types"),
)


class DocumentRepository:
    def __init__(self, session: Session):
        self._session = session

    def exists(self, filename: str) -> bool:
        return self._session.query(Document).filter(Document.filename == filename).first() is not None

    def insert(self, data: dict, chunks: list[str], embeddings: list[list[float]]) -> Document | None:
        if self.exists(data["filename"]):
            return None

        doc = Document(
            filename=data["filename"],
            headline=data["headline"],
            importance_score=data["importance_score"],
            reason=data["reason"],
            metadata_=data.get("metadata"),
        )
        self._session.add(doc)
        self._session.flush()

        self._attach_lookups(doc, data)
        self._add_insights(doc.id, data.get("key_insights") or [])
        self._add_chunks(doc.id, chunks, embeddings)
        return doc

    def _attach_lookups(self, doc: Document, data: dict) -> None:
        for key, model, attr in LOOKUPS:
            for name in data.get(key) or []:
                getattr(doc, attr).append(get_or_create(self._session, model, name))

    def _add_insights(self, document_id: int, insights: list[str]) -> None:
        self._session.add_all(
            DocumentKeyInsight(document_id=document_id, position=i, insight_text=insight)
            for i, insight in enumerate(insights)
        )

    def _add_chunks(self, document_id: int, chunks: list[str], embeddings: list[list[float]]) -> None:
        self._session.add_all(
            DocumentChunk(document_id=document_id, chunk_index=i, chunk_text=ct, embedding=emb)
            for i, (ct, emb) in enumerate(zip(chunks, embeddings))
        )
