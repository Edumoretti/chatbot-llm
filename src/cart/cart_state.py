from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from decimal import Decimal
import json

@dataclass
class CartItem:
    product_id: str
    name: str
    price: Decimal
    quantity: int
    image_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': str(self.price),
            'quantity': self.quantity,
            'image_url': self.image_url
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CartItem':
        return cls(
            product_id=data['product_id'],
            name=data['name'],
            price=Decimal(data['price']),
            quantity=data['quantity'],
            image_url=data.get('image_url')
        )

class CartState:
    def __init__(self):
        self.carts: Dict[str, Dict[str, CartItem]] = {}
        self.last_modified: Dict[str, datetime] = {}
    
    def get_cart(self, user_id: str) -> Dict[str, CartItem]:
        """
        Obtém o carrinho de um usuário específico
        """
        if user_id not in self.carts:
            self.carts[user_id] = {}
            self.last_modified[user_id] = datetime.now()
        return self.carts[user_id]
    
    def add_item(self, user_id: str, item: CartItem) -> None:
        """
        Adiciona ou atualiza um item no carrinho
        """
        cart = self.get_cart(user_id)
        if item.product_id in cart:
            cart[item.product_id].quantity += item.quantity
        else:
            cart[item.product_id] = item
        self.last_modified[user_id] = datetime.now()
    
    def remove_item(self, user_id: str, product_id: str) -> bool:
        """
        Remove um item do carrinho
        """
        cart = self.get_cart(user_id)
        if product_id in cart:
            del cart[product_id]
            self.last_modified[user_id] = datetime.now()
            return True
        return False
    
    def update_quantity(self, user_id: str, product_id: str, quantity: int) -> bool:
        """
        Atualiza a quantidade de um item no carrinho
        """
        cart = self.get_cart(user_id)
        if product_id in cart:
            if quantity > 0:
                cart[product_id].quantity = quantity
            else:
                del cart[product_id]
            self.last_modified[user_id] = datetime.now()
            return True
        return False
    
    def get_total(self, user_id: str) -> Decimal:
        """
        Calcula o total do carrinho
        """
        cart = self.get_cart(user_id)
        return sum(item.price * item.quantity for item in cart.values())
    
    def clear_cart(self, user_id: str) -> None:
        """
        Limpa o carrinho de um usuário
        """
        if user_id in self.carts:
            del self.carts[user_id]
            del self.last_modified[user_id]
