from abc import ABC, abstractmethod
from typing import Dict, Any
from src.orchestrator.orchestrator import DialogOrchestrator
from src.cart.cart import ShoppingCart
from src.checkout.checkout_handler import CheckoutHandler

class BaseWebhook(ABC):
    def __init__(
        self,
        orchestrator: DialogOrchestrator,
        shopping_cart: ShoppingCart,
        checkout_handler: CheckoutHandler
    ):
        self.orchestrator = orchestrator
        self.shopping_cart = shopping_cart
        self.checkout_handler = checkout_handler
    
    @abstractmethod
    async def handle_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagens recebidas do canal específico
        """
        pass
    
    @abstractmethod
    async def send_message(self, user_id: str, message: str, **kwargs) -> bool:
        """
        Envia mensagens para o canal específico
        """
        pass
    
    @abstractmethod
    async def send_product_card(self, user_id: str, product: Dict[str, Any]) -> bool:
        """
        Envia card de produto com imagem e botões de ação
        """
        pass

class WebhookError(Exception):
    pass
