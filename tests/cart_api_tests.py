import pytest
from fastapi.testclient import TestClient

def test_add_to_cart_endpoint(test_client, mock_product):
    response = test_client.post(
        f"/cart/user1/add",
        json={
            "product_id": mock_product["id"],
            "quantity": 2
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "cart_total" in data

def test_get_cart_endpoint(test_client):
    response = test_client.get("/cart/user1")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_metrics_endpoint(test_client):
    response = test_client.get("/metrics")
    
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert "orders" in data

def test_process_message_endpoint(test_client):
    response = test_client.post(
        "/message",
        json={
            "user_id": "user1",
            "message": "olá",
            "channel": "whatsapp"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
