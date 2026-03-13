from contextlib import contextmanager
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


_sync_engine = create_engine(settings.database_url_sync, echo=False)
_sync_session_factory = sessionmaker(bind=_sync_engine, expire_on_commit=False)


@contextmanager
def get_sync_db_session() -> Generator[Session, None, None]:
    session = _sync_session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
