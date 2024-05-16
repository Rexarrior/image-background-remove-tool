from fastapi import Depends
import pytest
from fastapi.testclient import TestClient
from carvekit.web.routers.account import api_router
from unittest.mock import MagicMock
from carvekit.web.database.managers import DBSingleton
from carvekit.web.schemas.config import WebAPIConfig

@pytest.fixture
def client():
    return TestClient(api_router)

@pytest.fixture
def account_test_data(): 
    return {
        "user_id": "test_user",
        "name": "Test User", 
        "token": "test_token",
        "credits": 0,
        }

@pytest.fixture
def config():
    return WebAPIConfig()

def test_account_authentication_failed(client):
    response = client.get("/account")
    assert response.status_code == 403
    assert response.json() == {"errors": [{"title": "Authentication failed"}]}


def test_account_successful(client):
    mock_db_manager = MagicMock()
    mock_db_manager.get_session.return_value.__enter__.return_value = MagicMock()
    mock_db_manager.accounts.calculate_personal_credits.return_value = 10
    mock_db_manager.subscriptions.calculate_subscription_credits_by_token.return_value = 20
    mock_db_manager.accounts.calculate_enterprise_credits.return_value = 30
    api_router.dependencies.append(Depends(lambda: mock_db_manager))

    response = client.get("/account", headers={"x_api_key": "valid_auth_token"})
    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "attributes": {
                "credits": {
                    "total": 60,
                    "subscription": 20,
                    "personal": 10,
                    "enterprise": 30
                },
                "api": {"free_calls": 99999, "sizes": "all"}
            }
        }
    }


def test_create_account(client, config, account_test_data):
    response = client.post("/account", json=account_test_data)
    assert response.status_code == 200
    assert response.json() == account_test_data


def test_update_account(client):
    response = client.put("/account/test_token", json={"name": "Updated User"})
    assert response.status_code == 200
    assert response.json() == {"name": "Updated User"}


def test_delete_account(client):
    response = client.delete("/account/test_token")
    assert response.status_code == 200
    assert response.json() == {"message": "Account deleted successfully"}


def test_reserve_credits(client):
    response = client.post("/account/reserve", json={"user_id": 123, "credits": 50, "credits_type": "personal"})
    assert response.status_code == 200
    assert response.json() == {"message": "Credits reserved successfully"}


def test_cancel_reservation(client):
    response = client.post("/account/cancel-reservation/123")
    assert response.status_code == 200
    assert response.json() == {"message": "Reservation cancelled successfully"}
