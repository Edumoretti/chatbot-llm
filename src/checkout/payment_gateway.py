from typing import Dict, Any, Optional
from decimal import Decimal
import aiohttp
from enum import Enum
from dataclasses import dataclass
from ..config import PAYMENT_GATEWAY_URL, PAYMENT_GATEWAY_KEY

class PaymentStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ERROR = "error"

@dataclass
class PaymentRequest:
    amount: Decimal
    currency: str
    order_id: str
    customer_id: str
    payment_method: str
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'amount': str(self.amount),
            'currency': self.currency,
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'payment_method': self.payment_method,
            'description': self.description
        }

class PaymentGateway:
    def __init__(self):
        self.base_url = PAYMENT_GATEWAY_URL
        self.api_key = PAYMENT_GATEWAY_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    async def create_payment(self, payment_request: PaymentRequest) -> Dict[str, Any]:
        """
        Cria uma nova transação de pagamento
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/payments",
                json=payment_request.to_dict(),
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                raise PaymentError(f"Erro ao criar pagamento: {await response.text()}")
    
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """
        Verifica o status de um pagamento
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/payments/{payment_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return PaymentStatus(data['status'])
                raise PaymentError(f"Erro ao verificar status do pagamento: {await response.text()}")

class PaymentError(Exception):
    pass
