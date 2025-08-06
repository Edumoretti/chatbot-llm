import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.catalog.catalog_api import CatalogAPI
from src.analytics.analytics import AnalyticsManager
from src.cart.cart import ShoppingCart
from typing import Dict, Any
import asyncio

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_product() -> Dict[str, Any]:
    return {
        "id": "test-product-1",
        "name": "Produto Teste",
        "price": "99.99",
        "image_url": "http://example.com/image.jpg"
    }

@pytest.fixture
def mock_catalog_api(mock_product):
    class MockCatalogAPI(CatalogAPI):
        async def get_product(self, product_id: str):
            if product_id == mock_product["id"]:
                return mock_product
            return None
        
        async def search_products(self, query: str):
            return [mock_product] if query in mock_product["name"] else []
    
    return MockCatalogAPI()

@pytest.fixture
def mock_analytics():
    class MockAnalytics(AnalyticsManager):
        def __init__(self):
            self.events = []
            self.errors = []
        
        def track_event(self, *args, **kwargs):
            self.events.append((args, kwargs))
        
        def track_error(self, *args, **kwargs):
            self.errors.append((args, kwargs))
    
    return MockAnalytics()

@pytest.fixture
def shopping_cart(mock_catalog_api):
    return ShoppingCart(mock_catalog_api)

# Fixture para lidar com loops assíncronos nos tests
@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
