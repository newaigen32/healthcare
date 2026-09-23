from collections.abc import Generator
import logging
import time

from fastapi import HTTPException, status

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import Settings

logger = logging.getLogger(__name__)



class Base(DeclarativeBase):
    pass


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine | None:
    return _engine


def get_session_factory() -> sessionmaker[Session] | None:
    return _SessionLocal


def configure_engine(database_url: str) -> Engine:
    global _engine, _SessionLocal
    kwargs: dict[str, object] = {"pool_pre_ping": True}
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
        kwargs["poolclass"] = StaticPool
    _engine = create_engine(database_url, **kwargs)
    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, expire_on_commit=False)
    return _engine


def reset_engine() -> None:
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def get_db() -> Generator[Session, None, None]:
    if _SessionLocal is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


def ping_database() -> None:
    if _engine is None:
        raise RuntimeError("Database is not configured.")
    with _engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def init_database(settings: Settings) -> None:
    from app.db.seed import seed_documents

    if not settings.database_url:
        return

    last_error: Exception | None = None
    engine: Engine | None = None
    for attempt in range(1, 11):
        try:
            engine = configure_engine(settings.database_url)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            last_error = None
            break
        except OperationalError as exc:
            last_error = exc
            logger.warning("Waiting for PostgreSQL (attempt %s/10)", attempt)
            time.sleep(2)
    if last_error is not None or engine is None:
        logger.error("Could not connect to PostgreSQL after retries")
        raise last_error or RuntimeError("Could not connect to the database.")

    Base.metadata.create_all(bind=engine)
    if settings.app_env.lower() == "production":
        logger.info("Skipping document seed because APP_ENV=production")
        return
    if _SessionLocal is None:
        return
    session = _SessionLocal()
    try:
        inserted = seed_documents(session)
        logger.info("Document seed complete; inserted %s new rows", inserted)
    finally:
        session.close()
