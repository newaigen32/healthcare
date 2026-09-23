from pathlib import Path
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# API tests import create_app(), which reads SEARCH_PROVIDER at import time.
# Docker/runtime still use postgres via compose and .env files.
os.environ.setdefault("SEARCH_PROVIDER", "mock")

SCRIPTS = Path(__file__).resolve().parents[2] / "database" / "scripts"


def _run_sql_file(session: Session, name: str) -> None:
    sql = (SCRIPTS / name).read_text(encoding="utf-8")
    raw = session.connection().connection
    raw.executescript(sql)
    session.commit()


@pytest.fixture
def session() -> Session:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    db_session = factory()
    _run_sql_file(db_session, "01_create_tables.sql")
    _run_sql_file(db_session, "02_insert_sample_data.sql")
    try:
        yield db_session
    finally:
        db_session.close()
        engine.dispose()


@pytest.fixture
def session_factory(session: Session) -> sessionmaker[Session]:
    return sessionmaker(bind=session.get_bind(), expire_on_commit=False)
