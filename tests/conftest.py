import os
import tempfile

# Configure the environment BEFORE the app is imported. Real env vars beat any local .env file.
_tmp_db = os.path.join(tempfile.mkdtemp(prefix="luweero-tests-"), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db}"
os.environ["STORAGE_PUBLIC_BASE_URL"] = "https://storage.example.test/blueprints"
os.environ["STORAGE_USE_SIGNED_URLS"] = "false"
os.environ["WEBHOOK_SHARED_SECRET"] = ""

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
