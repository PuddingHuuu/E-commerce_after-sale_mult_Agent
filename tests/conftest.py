import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TEST_DB = Path(__file__).resolve().parent / "test_after_sale.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB.as_posix()}"
os.environ["LLM_API_KEY"] = ""
os.environ["LLM_FALLBACK_ENABLED"] = "true"
os.environ["PLATFORM_REGISTER_INVITE_CODE"] = "TEST-PLATFORM-INVITE"

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def auth_headers(client):
    def login(role: str, login_name: str, password: str) -> dict[str, str]:
        response = client.post(
            "/api/v1/auth/login",
            json={
                "role": role,
                "login_name": login_name,
                "password": password,
                "remember": True,
            },
        )
        assert response.status_code == 200, response.text
        return {"Authorization": f"Bearer {response.json()['token']}"}

    return {
        "consumer": login("consumer", "13812345678", "Demo1234"),
        "platform": login("platform", "agent01", "Platform1234"),
        "merchant": login("merchant", "merchant01", "Merchant1234"),
    }
