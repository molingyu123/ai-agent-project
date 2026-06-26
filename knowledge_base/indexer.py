from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Iterable

from core.database import DocumentRecord, session_scope
from knowledge_base.retriever import get_retriever

logger = logging.getLogger(__name__)


class KnowledgeIndexer:
    """Indexes raw text or records into the configured vector store."""

    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 160):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.retriever = get_retriever()

    def index_text(
        self,
        text: str,
        source: str,
        title: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        clean_text = text.strip()
        if not clean_text:
            return {"indexed": 0, "skipped": 1, "reason": "empty text"}

        content_hash = self._hash(clean_text)
        metadata = metadata or {}
        chunks = self._chunk(clean_text)
        metadatas = [
            {
                **metadata,
                "source": source,
                "title": title,
                "content_hash": content_hash,
                "chunk_index": index,
            }
            for index, _ in enumerate(chunks)
        ]

        with session_scope() as session:
            existing = (
                session.query(DocumentRecord)
                .filter(DocumentRecord.content_hash == content_hash)
                .one_or_none()
            )
            if existing is not None:
                return {"indexed": 0, "skipped": len(chunks), "reason": "duplicate document"}

            ids = self.retriever.add_texts(chunks, metadatas=metadatas)
            session.add(
                DocumentRecord(
                    source=source,
                    title=title,
                    content_hash=content_hash,
                    metadata_json={**metadata, "chunk_count": len(chunks), "vector_ids": ids},
                )
            )

        return {"indexed": len(chunks), "skipped": 0, "content_hash": content_hash}

    def index_records(
        self,
        records: Iterable[dict[str, Any]],
        source: str,
        title_field: str | None = None,
    ) -> dict[str, int]:
        indexed = 0
        skipped = 0
        for record in records:
            text = self._record_to_text(record)
            title = str(record.get(title_field)) if title_field and record.get(title_field) else None
            result = self.index_text(text, source=source, title=title, metadata={"record": record})
            indexed += result.get("indexed", 0)
            skipped += result.get("skipped", 0)
        return {"indexed": indexed, "skipped": skipped}

    def index_directory(self, directory: str | Path, glob: str = "*.md") -> dict[str, int]:
        root = Path(directory)
        indexed = 0
        skipped = 0
        for path in root.rglob(glob):
            result = self.index_text(
                path.read_text(encoding="utf-8"),
                source=str(path),
                title=path.name,
                metadata={"path": str(path)},
            )
            indexed += result.get("indexed", 0)
            skipped += result.get("skipped", 0)
        return {"indexed": indexed, "skipped": skipped}

    def _chunk(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        chunks: list[str] = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunks.append(text[start:end])
            if end == len(text):
                break
            start = max(end - self.chunk_overlap, start + 1)
        return chunks

    def _record_to_text(self, record: dict[str, Any]) -> str:
        return "\n".join(f"{key}: {value}" for key, value in record.items() if value is not None)

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
