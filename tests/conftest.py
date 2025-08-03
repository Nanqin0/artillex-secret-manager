import os
import base64
import secrets
import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient


@pytest.fixture(scope="session")
def mongo():
    """
    Session-scoped MongoDB client pointing at the local Docker container.
    Fails fast if Mongo isn't reachable.
    """
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(uri)
    try:
        client.admin.command("ping")
    except Exception as e:
        raise RuntimeError(
            f"Mongo not reachable at {uri}. Start it first: `docker start mongo`"
        ) from e
    yield client
    client.close()


@pytest.fixture(autouse=True)
def clear_db(mongo):
    """
    Clean test collections before and after each test to avoid cross-test bleed.
    """
    db = mongo["vault"]
    db["secrets"].delete_many({})
    db["audit_logs"].delete_many({})
    yield
    db["secrets"].delete_many({})
    db["audit_logs"].delete_many({})


@pytest.fixture(scope="session")
def app_client(mongo):
    """
    FastAPI TestClient that exercises the real app with lifespan
    (so it connects to Mongo). We set env vars BEFORE importing the app.
    """
    os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
    # 32-byte random key, base64-encoded (matches your app's requirement)
    os.environ.setdefault(
        "MASTER_KEY",
        base64.b64encode(secrets.token_bytes(32)).decode(),
    )
    os.environ.setdefault("AUDIT_ENABLED", "true")
    os.environ.setdefault("AUDIT_TTL_DAYS", "0")

    # Import AFTER env vars are set so your config/lifespan reads them.
    from app.main import app

    with TestClient(app) as client:
        yield client
