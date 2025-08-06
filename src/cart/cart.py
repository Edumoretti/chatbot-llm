from typing import List, Optional, Dict, Any
from decimal import Decimal
from .cart_state import CartState, CartItem
from ..catalog.catalog_api import CatalogAPI

class ShoppingCart:
    def __init__(self, catalog_api: CatalogAPI):
        self.state = CartState()
        self.catalog_api = catalog_api
    
    async def add_to_cart(
        self,
        user_id: str,
        product_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Adiciona um produto ao carrinho
        """
        # Busca informações do produto no catálogo
        product = await self.catalog_api.get_product(product_id)
        if not product:
            raise ValueError(f"Produto não encontrado: {product_id}")
        
        item = CartItem(
            product_id=product_id,
            name=product['name'],
            price=Decimal(str(product['price'])),
            quantity=quantity,
            image_url=product.get('image_url')
        )
        
        self.state.add_item(user_id, item)
        
        return {
            'message': f"Adicionado {quantity}x {product['name']} ao carrinho",
            'cart_total': str(self.state.get_total(user_id))
        }
    
    async def remove_from_cart(
        self,
        user_id: str,
        product_id: str
    ) -> Dict[str, Any]:
        """
        Remove um produto do carrinho
        """
        if self.state.remove_item(user_id, product_id):
            return {
                'message': "Item removido do carrinho",
                'cart_total': str(self.state.get_total(user_id))
            }
        raise ValueError("Item não encontrado no carrinho")
    
    async def update_quantity(
        self,
        user_id: str,
        product_id: str,
        quantity: int
    ) -> Dict[str, Any]:
        """
        Atualiza a quantidade de um produto no carrinho
        """
        if self.state.update_quantity(user_id, product_id, quantity):
            return {
                'message': f"Quantidade atualizada para {quantity}",
                'cart_total': str(self.state.get_total(user_id))
            }
        raise ValueError("Item não encontrado no carrinho")
    
    def get_cart_items(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retorna os itens no carrinho
        """
        cart = self.state.get_cart(user_id)
        return [item.to_dict() for item in cart.values()]
    
    def get_cart_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Retorna um resumo do carrinho
        """
        items = self.get_cart_items(user_id)
        total = self.state.get_total(user_id)
        
        return {
            'items': items,
            'total': str(total),
            'item_count': len(items),
            'total_quantity': sum(item['quantity'] for item in items)
        }
    
    def clear_cart(self, user_id: str) -> Dict[str, Any]:
        """
        Limpa o carrinho do usuário
        """
        self.state.clear_cart(user_id)
        return {'message': "Carrinho limpo com sucesso"}
