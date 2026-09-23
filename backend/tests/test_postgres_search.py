import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Document
from app.db.seed import SAMPLE_DOCUMENTS, seed_documents
from app.services.postgres_search import PostgresSearchProvider


@pytest.mark.asyncio
async def test_postgres_search_returns_matching_documents(session_factory) -> None:
    provider = PostgresSearchProvider(session_factory)
    results = await provider.search("MRI", top=10)
    assert results
    assert any("MRI" in result.title or "MRI" in result.content for result in results)
    assert all(result.id for result in results)


@pytest.mark.asyncio
async def test_postgres_search_returns_empty_when_nothing_matches(session_factory) -> None:
    provider = PostgresSearchProvider(session_factory)
    results = await provider.search("zzzznotfoundxyz", top=10)
    assert results == []


def test_seed_does_not_create_duplicate_records(session: Session) -> None:
    first_count = len(session.scalars(select(Document.id)).all())
    inserted = seed_documents(session)
    second_count = len(session.scalars(select(Document.id)).all())
    assert inserted == 0
    assert first_count == second_count
    assert first_count == len(SAMPLE_DOCUMENTS)
