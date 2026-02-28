from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from db.models import Base
from utils import DATABASE_URL


class Database:
    def __init__(self, url: str | None = None) -> None:
        self._url = url or DATABASE_URL
        if not self._url:
            raise ValueError("DATABASE_URL is required")
        self._engine = create_engine(
            self._url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    def create_tables(self) -> None:
        with self._engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
