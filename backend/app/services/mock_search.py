import re

from app.schemas.search import SearchResult
from app.services.search_provider import SearchProvider

MOCK_DOCUMENTS: list[SearchResult] = [
    SearchResult(
        id="1",
        title="Denied Claims Procedure",
        content="If a claim is denied because of missing documentation...",
        source="Claims-SOP-2026.pdf",
        category="SOP",
        score=0.92,
    ),
    SearchResult(
        id="2",
        title="Payer Appeal Windows",
        content="Most commercial payers allow 30 to 180 days...",
        source="Payer-Rules-Guide.pdf",
        category="Payer Rules",
        score=0.81,
    ),
    SearchResult(
        id="3",
        title="Previous Case: Missing Prior Authorization",
        content="Case 4412 was denied for missing prior authorization...",
        source="Case-Notes-4412.docx",
        category="Previous Cases",
        score=0.74,
    ),
]


class MockSearchProvider(SearchProvider):
    """In-memory documents used until Azure AI Search is connected."""

    async def search(self, query: str, top: int) -> list[SearchResult]:
        tokens = [token for token in re.findall(r"[a-z0-9]+", query.lower()) if len(token) > 1]
        if not tokens:
            return []

        matches = [document for document in MOCK_DOCUMENTS if _matches(document, tokens)]
        if not matches:
            return []
        # Demo catalog: a match returns the current mock set so the UI can show
        # multiple source cards. Azure search will rank real chunks later.
        return MOCK_DOCUMENTS[:top]


def _matches(document: SearchResult, tokens: list[str]) -> bool:
    haystack = " ".join(
        [
            document.id,
            document.title,
            document.content,
            document.source,
            document.category or "",
        ]
    ).lower()
    return any(token in haystack for token in tokens)
