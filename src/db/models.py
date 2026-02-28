from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from utils import OPENAI_EMBEDDING_DIMENSIONS


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    headline: Mapped[str] = mapped_column(Text, nullable=False)
    importance_score: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("importance_score >= 0 AND importance_score <= 100"),
        nullable=False,
        index=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)

    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="document_tags",
        back_populates="documents",
    )
    power_mentions: Mapped[list["PowerMention"]] = relationship(
        "PowerMention",
        secondary="document_power_mentions",
        back_populates="documents",
    )
    agencies: Mapped[list["Agency"]] = relationship(
        "Agency",
        secondary="document_agencies",
        back_populates="documents",
    )
    lead_types: Mapped[list["LeadType"]] = relationship(
        "LeadType",
        secondary="document_lead_types",
        back_populates="documents",
    )
    key_insights: Mapped[list["DocumentKeyInsight"]] = relationship(
        "DocumentKeyInsight",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        secondary="document_tags",
        back_populates="tags",
    )


class PowerMention(Base):
    __tablename__ = "power_mentions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        secondary="document_power_mentions",
        back_populates="power_mentions",
    )


class Agency(Base):
    __tablename__ = "agencies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        secondary="document_agencies",
        back_populates="agencies",
    )


class LeadType(Base):
    __tablename__ = "lead_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)

    documents: Mapped[list["Document"]] = relationship(
        "Document",
        secondary="document_lead_types",
        back_populates="lead_types",
    )


class DocumentTag(Base):
    __tablename__ = "document_tags"
    __table_args__ = (UniqueConstraint("document_id", "tag_id", name="uq_document_tag"),)

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
    )


class DocumentPowerMention(Base):
    __tablename__ = "document_power_mentions"
    __table_args__ = (UniqueConstraint("document_id", "power_mention_id", name="uq_document_power_mention"),)

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    power_mention_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("power_mentions.id", ondelete="CASCADE"),
        primary_key=True,
    )


class DocumentAgency(Base):
    __tablename__ = "document_agencies"
    __table_args__ = (UniqueConstraint("document_id", "agency_id", name="uq_document_agency"),)

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    agency_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("agencies.id", ondelete="CASCADE"),
        primary_key=True,
    )


class DocumentLeadType(Base):
    __tablename__ = "document_lead_types"
    __table_args__ = (UniqueConstraint("document_id", "lead_type_id", name="uq_document_lead_type"),)

    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    )
    lead_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lead_types.id", ondelete="CASCADE"),
        primary_key=True,
    )


class DocumentKeyInsight(Base):
    __tablename__ = "document_key_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    insight_text: Mapped[str] = mapped_column(Text, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="key_insights")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(OPENAI_EMBEDDING_DIMENSIONS), nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk"),
        Index(
            "ix_document_chunks_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
