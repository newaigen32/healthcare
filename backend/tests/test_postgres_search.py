import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.postgres_search import PostgresSearchProvider
from tests.conftest import _run_sql_file


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


def test_sample_data_script_is_idempotent(session: Session) -> None:
    first_count = session.execute(text("SELECT COUNT(*) FROM documents")).scalar_one()
    _run_sql_file(session, "02_insert_sample_data.sql")
    second_count = session.execute(text("SELECT COUNT(*) FROM documents")).scalar_one()
    assert first_count == 15
    assert second_count == first_count
