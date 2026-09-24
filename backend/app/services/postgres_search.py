from collections.abc import Mapping
import logging
import re

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

STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "about",
        "do",
        "does",
        "explain",
        "for",
        "how",
        "in",
        "is",
        "me",
        "of",
        "on",
        "or",
        "please",
        "tell",
        "the",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
    }
)

FIELD_MATCH = """(
    id {op} :{name} ESCAPE '\\'
    OR title {op} :{name} ESCAPE '\\'
    OR COALESCE(summary, '') {op} :{name} ESCAPE '\\'
    OR content {op} :{name} ESCAPE '\\'
    OR document_type {op} :{name} ESCAPE '\\'
)"""


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
        tokens = _search_tokens(query)
        if not tokens:
            return []
        try:
            with self._session_factory() as session:
                dialect = session.get_bind().dialect.name if session.get_bind() is not None else "postgresql"
                operator = "ILIKE" if dialect == "postgresql" else "LIKE"
                sql, params = _build_search_sql(tokens, top, operator)
                rows = session.execute(text(sql), params).mappings().all()
        except Exception as exc:
            logger.error("PostgreSQL search failed: %s", type(exc).__name__)
            raise SearchUpstreamError("Database search is unavailable.") from exc

        return [_to_search_result(row) for row in rows]


def _search_tokens(query: str) -> list[str]:
    normalized = query.strip().replace("’", "'").replace("‘", "'")
    normalized = re.sub(r"'s\b", "", normalized, flags=re.IGNORECASE)
    parts = re.findall(r"[A-Za-z0-9-]+", normalized)
    tokens = [part for part in parts if part.lower() not in STOPWORDS and len(part) >= 2]
    if tokens:
        return tokens
    leftover = re.sub(r"[^\w\s-]+", " ", normalized).strip()
    return [leftover] if leftover else []


def _build_search_sql(tokens: list[str], top: int, operator: str) -> tuple[str, dict[str, object]]:
    params: dict[str, object] = {"top": top, "overview": "%overview%"}
    clauses: list[str] = []
    for index, token in enumerate(tokens):
        name = f"p{index}"
        params[name] = f"%{_escape_like(token)}%"
        clauses.append(FIELD_MATCH.format(op=operator, name=name))
    where_sql = " AND ".join(clauses)
    sql = f"""
SELECT id, title, document_type, source, summary, content
FROM documents
WHERE {where_sql}
ORDER BY
  CASE
    WHEN title {operator} :p0 ESCAPE '\\' AND title {operator} :overview ESCAPE '\\' THEN 0
    WHEN title {operator} :p0 ESCAPE '\\' THEN 1
    WHEN document_type {operator} :p0 ESCAPE '\\' THEN 2
    ELSE 3
  END,
  title
LIMIT :top
"""
    return sql, params


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
