from typing import Dict, Any, Optional
from decimal import Decimal
import uuid
from datetime import datetime
from .payment_gateway import PaymentGateway, PaymentRequest, PaymentStatus
from ..cart.cart import ShoppingCart

class CheckoutHandler:
    def __init__(self, shopping_cart: ShoppingCart, payment_gateway: PaymentGateway):
        self.shopping_cart = shopping_cart
        self.payment_gateway = payment_gateway
        self.checkout_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def create_checkout_session(
        self,
        user_id: str,
        payment_method: str,
        currency: str = "BRL"
    ) -> Dict[str, Any]:
        """
        Cria uma nova sessão de checkout
        """
        # Obtém o carrinho atual
        cart_summary = self.shopping_cart.get_cart_summary(user_id)
        if not cart_summary['items']:
            raise CheckoutError("Carrinho vazio")
        
        # Gera ID único para o pedido
        order_id = str(uuid.uuid4())
        
        # Cria sessão de checkout
        checkout_session = {
            'order_id': order_id,
            'user_id': user_id,
            'items': cart_summary['items'],
            'total': cart_summary['total'],
            'currency': currency,
            'payment_method': payment_method,
            'status': 'created',
            'created_at': datetime.now().isoformat(),
        }
        
        self.checkout_sessions[order_id] = checkout_session
        
        return checkout_session
    
    async def process_payment(self, order_id: str) -> Dict[str, Any]:
        """
        Processa o pagamento de uma sessão de checkout
        """
        session = self.checkout_sessions.get(order_id)
        if not session:
            raise CheckoutError("Sessão de checkout não encontrada")
        
        if session['status'] != 'created':
            raise CheckoutError("Sessão de checkout já processada")
        
        try:
            # Cria requisição de pagamento
            payment_request = PaymentRequest(
                amount=Decimal(session['total']),
                currency=session['currency'],
                order_id=session['order_id'],
                customer_id=session['user_id'],
                payment_method=session['payment_method'],
                description=f"Pedido {session['order_id']}"
            )
            
            # Processa pagamento
            payment_result = await self.payment_gateway.create_payment(payment_request)
            
            # Atualiza status da sessão
            session['status'] = 'processing'
            session['payment_id'] = payment_result['payment_id']
            session['payment_url'] = payment_result.get('payment_url')
            
            return {
                'order_id': session['order_id'],
                'status': session['status'],
                'payment_url': session['payment_url'],
                'total': session['total']
            }
            
        except Exception as e:
            session['status'] = 'error'
            session['error'] = str(e)
            raise CheckoutError(f"Erro ao processar pagamento: {str(e)}")
    
    async def verify_payment_status(self, order_id: str) -> Dict[str, Any]:
        """
        Verifica o status do pagamento de uma sessão
        """
        session = self.checkout_sessions.get(order_id)
        if not session:
            raise CheckoutError("Sessão de checkout não encontrada")
        
        if 'payment_id' not in session:
            raise CheckoutError("Pagamento ainda não iniciado")
        
        try:
            status = await self.payment_gateway.get_payment_status(session['payment_id'])
            
            if status == PaymentStatus.APPROVED:
                # Limpa o carrinho após pagamento aprovado
                self.shopping_cart.clear_cart(session['user_id'])
            
            session['status'] = status.value
            
            return {
                'order_id': session['order_id'],
                'status': status.value,
                'total': session['total']
            }
            
        except Exception as e:
            raise CheckoutError(f"Erro ao verificar status do pagamento: {str(e)}")

class CheckoutError(Exception):
    pass
