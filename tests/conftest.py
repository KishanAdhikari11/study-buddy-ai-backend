from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Basic TestClient for making HTTP requests"""
    return TestClient(app)


@pytest.fixture(scope="function")
def mock_auth_service():
    """Mock for AuthService"""
    mock = AsyncMock()
    successful_auth = {
        "user": {
            "id": "test-user-uuid-12345",
            "email": "test@example.com",
            "user_metadata": {"full_name": "Test User"},
            "created_at": "2026-04-16T00:00:00Z",
        },
        "session": {
            "access_token": "fake.access.token.jwt",
            "refresh_token": "fake.refresh.token",
        },
    }

    mock.signup.return_value = successful_auth
    mock.login.return_value = successful_auth
    mock.oauth_login.return_value = {"auth_url": "https://fake-auth-url.com"}
    mock.handle_oauth_callback.return_value = successful_auth
    mock.logout.return_value = None
    mock.request_password_reset.return_value = None
    mock.update_password.return_value = None

    return mock
