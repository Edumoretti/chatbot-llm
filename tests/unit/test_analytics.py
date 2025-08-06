import pytest
from src.analytics.analytics import AnalyticsManager, EventType
from decimal import Decimal

def test_track_message(mock_analytics):
    mock_analytics.track_message(
        user_id="user1",
        message="olá",
        channel="whatsapp",
        is_incoming=True
    )
    
    assert len(mock_analytics.events) == 1
    event = mock_analytics.events[0]
    assert event[0][0] == EventType.MESSAGE_RECEIVED
    assert event[1]["user_id"] == "user1"

def test_track_cart_update(mock_analytics):
    cart_data = {
        "items": [
            {
                "product_id": "123",
                "quantity": 2,
                "price": "10.00"
            }
        ],
        "total": "20.00"
    }
    
    mock_analytics.track_cart_update(
        user_id="user1",
        cart_data=cart_data,
        channel="api"
    )
    
    assert len(mock_analytics.events) == 1
    assert mock_analytics.events[0][0][0] == EventType.CART_UPDATED

def test_track_error(mock_analytics):
    error = ValueError("Teste de erro")
    mock_analytics.track_error(
        error=error,
        user_id="user1",
        context={"action": "test"}
    )
    
    assert len(mock_analytics.errors) == 1
    error_event = mock_analytics.errors[0]
    assert isinstance(error_event[0][0], ValueError)
