from rcs.config import get_settings
from rcs.db import session as db_session


def test_session_uses_postgres_url():
    assert "postgresql+asyncpg" in get_settings().database_url


def test_session_factory_present():
    assert hasattr(db_session, "session")


def test_no_memory_branch_in_config():
    s = get_settings()
    # memory/sqlite storage fields must be gone
    assert not hasattr(s, "storage")
    assert not hasattr(s, "db_path")