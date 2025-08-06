import pytest
from fastapi.testclient import TestClient

def test_complete_checkout_flow(test_client, mock_product):
    # 1. Adiciona produto ao carrinho
    cart_response = test_client.post(
        f"/cart/user1/add",
        json={
            "product_id": mock_product["id"],
            "quantity": 1
        }
    )
    assert cart_response.status_code == 200
    
    # 2. Verifica o carrinho
    cart = test_client.get("/cart/user1")
    assert cart.status_code == 200
    assert len(cart.json()["items"]) == 1
    
    # 3. Inicia checkout
    checkout_response = test_client.post(
        "/checkout/user1/create",
        json={
            "payment_method": "credit_card",
            "currency": "BRL"
        }
    )
    assert checkout_response.status_code == 200
    order_id = checkout_response.json()["order_id"]
    
    # 4. Processa pagamento
    payment_response = test_client.post(f"/checkout/{order_id}/process")
    assert payment_response.status_code == 200
    
    # 5. Verifica status final
    status_response = test_client.get(f"/checkout/{order_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] in ["approved", "processing"]
