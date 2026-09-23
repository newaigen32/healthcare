from collections.abc import Mapping
import logging

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import SearchUpstreamError
from app.schemas.search import SearchResult
from app.services.search_provider import SearchProvider

logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "SOP": "SOP",
    "PAYER_RULE": "Payer Rules",
    "PAST_CASE": "Previous Cases",
}

SEARCH_SQL = """
SELECT id, title, document_type, source, summary, content
FROM documents
WHERE id ILIKE :pattern ESCAPE '\\'
   OR title ILIKE :pattern ESCAPE '\\'
   OR COALESCE(summary, '') ILIKE :pattern ESCAPE '\\'
   OR content ILIKE :pattern ESCAPE '\\'
ORDER BY title
LIMIT :top
"""

SEARCH_SQL_LIKE = SEARCH_SQL.replace("ILIKE", "LIKE")


class PostgresSearchProvider(SearchProvider):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    async def ping(self) -> None:
        try:
            with self._session_factory() as session:
                session.execute(text("SELECT 1"))
        except Exception as exc:
            logger.error("PostgreSQL search health check failed: %s", type(exc).__name__)
            raise SearchUpstreamError("Database search is unavailable.") from exc

    async def search(self, query: str, top: int) -> list[SearchResult]:
        pattern = f"%{_escape_like(query.strip())}%"
        try:
            with self._session_factory() as session:
                dialect = session.get_bind().dialect.name if session.get_bind() is not None else "postgresql"
                sql = SEARCH_SQL if dialect == "postgresql" else SEARCH_SQL_LIKE
                rows = session.execute(text(sql), {"pattern": pattern, "top": top}).mappings().all()
        except Exception as exc:
            logger.error("PostgreSQL search failed: %s", type(exc).__name__)
            raise SearchUpstreamError("Database search is unavailable.") from exc

        return [_to_search_result(row) for row in rows]


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _to_search_result(row: Mapping[str, object]) -> SearchResult:
    summary = str(row.get("summary") or "").strip()
    content = str(row.get("content") or "").strip()
    document_type = str(row.get("document_type") or "")
    return SearchResult(
        id=str(row["id"]),
        title=str(row["title"]),
        content=summary or content,
        source=str(row.get("source") or "Unknown source"),
        category=CATEGORY_LABELS.get(document_type, document_type or None),
        score=None,
    )
