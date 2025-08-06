import pytest
from decimal import Decimal
from src.cart.cart import ShoppingCart
from src.cart.cart_state import CartItem

@pytest.mark.asyncio
async def test_add_to_cart(shopping_cart, mock_product):
    result = await shopping_cart.add_to_cart(
        user_id="user1",
        product_id=mock_product["id"],
        quantity=2
    )
    
    assert "message" in result
    assert "cart_total" in result
    assert Decimal(result["cart_total"]) == Decimal("199.98")

@pytest.mark.asyncio
async def test_add_invalid_product(shopping_cart):
    with pytest.raises(ValueError):
        await shopping_cart.add_to_cart(
            user_id="user1",
            product_id="invalid-id"
        )

def test_get_cart_summary(shopping_cart):
    # Adiciona item diretamente ao estado
    item = CartItem(
        product_id="test-1",
        name="Test Product",
        price=Decimal("10.00"),
        quantity=2
    )
    shopping_cart.state.add_item("user1", item)
    
    summary = shopping_cart.get_cart_summary("user1")
    
    assert summary["total"] == "20.00"
    assert summary["item_count"] == 1
    assert summary["total_quantity"] == 2

@pytest.mark.asyncio
async def test_remove_from_cart(shopping_cart, mock_product):
    # Primeiro adiciona um item
    await shopping_cart.add_to_cart(
        user_id="user1",
        product_id=mock_product["id"]
    )
    
    # Depois remove
    result = await shopping_cart.remove_from_cart(
        user_id="user1",
        product_id=mock_product["id"]
    )
    
    assert result["cart_total"] == "0"
