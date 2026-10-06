"""
Test configuration and shared fixtures.

Uses an in-memory SQLite database so tests never touch the real Postgres DB.
The `get_db` dependency is overridden for every test via a session-scoped
engine + a function-scoped transaction that is rolled back after each test,
keeping tests fully isolated.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from app.db.session import Base, get_db
from app.main import create_app

# ---------------------------------------------------------------------------
# Engine — SQLite in-memory, shared pool so every connection sees same data
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///:memory:?check_same_thread=False"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# SQLite doesn't enforce FK constraints by default — turn them on
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ---------------------------------------------------------------------------
# Create all tables once per session
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Per-test DB session — rolls back after every test for full isolation
# ---------------------------------------------------------------------------
@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# FastAPI TestClient with the DB override applied
# ---------------------------------------------------------------------------
@pytest.fixture()
def client(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # rollback handled by db_session fixture

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ---------------------------------------------------------------------------
# Convenience helpers shared across test modules
# ---------------------------------------------------------------------------

def register_user(client: TestClient, username: str, email: str, password: str) -> dict:
    """Register a user and return the full JSON response body."""
    resp = client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert resp.status_code == 201, f"Register failed: {resp.text}"
    return resp.json()


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
