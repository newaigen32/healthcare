from app.schemas.search import SearchResult
from app.services.search_provider import SearchProvider

MOCK_DOCUMENTS: list[SearchResult] = [
    SearchResult(
        id="claims-sop-denied",
        title="Denied Claims Procedure",
        content=(
            "If a claim is denied because of missing documentation, notify the submitter "
            "within two business days and request the required records. Do not close the "
            "case until the documentation is received or the appeal window expires."
        ),
        source="Claims-SOP-2026.pdf",
        category="SOP",
        score=0.92,
    ),
    SearchResult(
        id="payer-rules-appeal",
        title="Payer Appeal Windows",
        content=(
            "Most commercial payers allow 30 to 180 days to appeal a denied claim. "
            "Confirm the payer-specific window in the contract file before submitting."
        ),
        source="Payer-Rules-Guide.pdf",
        category="Payer Rules",
        score=0.81,
    ),
    SearchResult(
        id="case-notes-missing-auth",
        title="Previous Case: Missing Prior Authorization",
        content=(
            "Case 4412 was denied for missing prior authorization. The team obtained "
            "retrospective auth and resubmitted with the original claim number."
        ),
        source="Case-Notes-4412.docx",
        category="Previous Cases",
        score=0.74,
    ),
]


class MockSearchProvider(SearchProvider):
    """Deterministic local results used when Azure Search is not configured."""

    async def search(self, query: str, top: int) -> list[SearchResult]:
        normalized = query.lower()
        ranked = [
            document
            for document in MOCK_DOCUMENTS
            if any(
                token in document.title.lower()
                or token in document.content.lower()
                or token in (document.category or "").lower()
                or token in document.source.lower()
                for token in normalized.split()
                if len(token) > 2
            )
        ]
        if not ranked:
            ranked = list(MOCK_DOCUMENTS)
        return ranked[:top]
