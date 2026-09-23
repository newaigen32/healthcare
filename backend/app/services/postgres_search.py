import logging

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.exceptions import SearchUpstreamError
from app.db.models import Document
from app.schemas.search import SearchResult
from app.services.search_provider import SearchProvider

logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "SOP": "SOP",
    "PAYER_RULE": "Payer Rules",
    "PAST_CASE": "Previous Cases",
}


class PostgresSearchProvider(SearchProvider):
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    async def ping(self) -> None:
        try:
            with self._session_factory() as session:
                session.execute(select(1))
        except Exception as exc:
            logger.error("PostgreSQL search health check failed: %s", type(exc).__name__)
            raise SearchUpstreamError("Database search is unavailable.") from exc

    async def search(self, query: str, top: int) -> list[SearchResult]:
        pattern = f"%{_escape_like(query.strip())}%"
        try:
            with self._session_factory() as session:
                statement = (
                    select(Document)
                    .where(
                        or_(
                            Document.title.ilike(pattern, escape="\\"),
                            Document.summary.ilike(pattern, escape="\\"),
                            Document.content.ilike(pattern, escape="\\"),
                        )
                    )
                    .order_by(Document.title)
                    .limit(top)
                )
                documents = session.scalars(statement).all()
        except Exception as exc:
            logger.error("PostgreSQL search failed: %s", type(exc).__name__)
            raise SearchUpstreamError("Database search is unavailable.") from exc

        return [_to_search_result(document) for document in documents]


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _to_search_result(document: Document) -> SearchResult:
    snippet = document.summary.strip() or document.content.strip()
    return SearchResult(
        id=document.id,
        title=document.title,
        content=snippet,
        source=document.source,
        category=CATEGORY_LABELS.get(document.document_type, document.document_type),
        score=None,
    )
