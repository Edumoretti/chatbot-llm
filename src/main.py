from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from .orchestrator.orchestrator import DialogOrchestrator
from .orchestrator.context_manager import ContextManager
from .cart.cart import ShoppingCart
from .catalog.catalog_api import CatalogAPI
from .checkout.checkout_handler import CheckoutHandler
from .checkout.payment_gateway import PaymentGateway
from .logs.analytics import AnalyticsManager

# Inicialização da aplicação
app = FastAPI(title="Shopping Bot API")

# Inicialização dos serviços
catalog_api = CatalogAPI()
orchestrator = DialogOrchestrator()
context_manager = ContextManager()
shopping_cart = ShoppingCart(catalog_api)
payment_gateway = PaymentGateway()
checkout_handler = CheckoutHandler(shopping_cart, payment_gateway)
analytics_manager = AnalyticsManager()


# Models
class MessageRequest(BaseModel):
    user_id: str
    message: str
    channel: str
    context: Optional[Dict[str, Any]] = None


class CartItemRequest(BaseModel):
    product_id: str
    quantity: int = 1


class CheckoutRequest(BaseModel):
    payment_method: str
    currency: str = "BRL"


# Rotas de Mensagens
@app.post("/message")
async def process_message(request: MessageRequest):
    try:
        # Registra a mensagem recebida
        analytics_manager.track_message(
            request.user_id,
            request.message,
            request.channel,
            is_incoming=True
        )

        # Atualiza o contexto se fornecido
        if request.context:
            context_manager.update_context(request.user_id, request.context)

        # Obtém o contexto atual
        current_context = context_manager.get_context(request.user_id)

        # Processa a mensagem
        response = await orchestrator.process_message(
            user_id=request.user_id,
            message=request.message,
            channel=request.channel,
            context=current_context
        )

        # Registra a resposta enviada
        analytics_manager.track_message(
            request.user_id,
            response,
            request.channel,
            is_incoming=False
        )

        return {"response": response}
    except Exception as e:
        analytics_manager.track_error(e, request.user_id, request.context)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/conversation/{user_id}")
async def clear_conversation(user_id: str):
    orchestrator.clear_conversation(user_id)
    context_manager.clear_context(user_id)
    return {"message": "Conversa limpa com sucesso"}


# Rotas do Carrinho
@app.post("/cart/{user_id}/add")
async def add_to_cart(user_id: str, item: CartItemRequest):
    try:
        result = await shopping_cart.add_to_cart(
            user_id,
            item.product_id,
            item.quantity
        )

        # Registra atualização do carrinho
        cart_summary = shopping_cart.get_cart_summary(user_id)
        analytics_manager.track_cart_update(user_id, cart_summary, "api")

        return result
    except Exception as e:
        analytics_manager.track_error(e, user_id)
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/cart/{user_id}/items/{product_id}")
async def remove_from_cart(user_id: str, product_id: str):
    try:
        result = await shopping_cart.remove_from_cart(user_id, product_id)

        # Registra atualização do carrinho
        cart_summary = shopping_cart.get_cart_summary(user_id)
        analytics_manager.track_cart_update(user_id, cart_summary, "api")

        return result
    except Exception as e:
        analytics_manager.track_error(e, user_id)
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/cart/{user_id}")
async def get_cart(user_id: str):
    try:
        cart_summary = shopping_cart.get_cart_summary(user_id)
        analytics_manager.track_cart_update(user_id, cart_summary, "api")
        return cart_summary
    except Exception as e:
        analytics_manager.track_error(e, user_id)
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/cart/{user_id}")
async def clear_cart(user_id: str):
    try:
        result = shopping_cart.clear_cart(user_id)
        analytics_manager.track_cart_update(user_id, {"items": []}, "api")
        return result
    except Exception as e:
        analytics_manager.track_error(e, user_id)
        raise HTTPException(status_code=400, detail=str(e))


# Rotas de Checkout
@app.post("/checkout/{user_id}/create")
async def create_checkout_session(user_id: str, checkout_request: CheckoutRequest):
    try:
        result = await checkout_handler.create_checkout_session(
            user_id,
            checkout_request.payment_method,
            checkout_request.currency
        )

        # Registra início do checkout
        analytics_manager.track_checkout(
            user_id,
            result['order_id'],
            float(result['total']),
            "api"
        )

        return result
    except Exception as e:
        analytics_manager.track_error(e, user_id)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/checkout/{order_id}/process")
async def process_checkout_payment(order_id: str):
    try:
        result = await checkout_handler.process_payment(order_id)

        # Registra conclusão do pedido se aprovado
        if result.get('status') == 'approved':
            analytics_manager.track_order_completion(
                result['user_id'],
                order_id,
                float(result['total']),
                "api"
            )

        return result
    except Exception as e:
        analytics_manager.track_error(e, context={"order_id": order_id})
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/checkout/{order_id}/status")
async def check_payment_status(order_id: str):
    try:
        return await checkout_handler.verify_payment_status(order_id)
    except Exception as e:
        analytics_manager.track_error(e, context={"order_id": order_id})
        raise HTTPException(status_code=400, detail=str(e))


# Rotas de Analytics
@app.get("/metrics")
async def get_metrics():
    """
    Retorna as métricas coletadas
    """
    return analytics_manager.get_metrics()


# Inicialização do servidor
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)