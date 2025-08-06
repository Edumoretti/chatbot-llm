from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json
from pathlib import Path

class EventType(Enum):
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    PRODUCT_VIEWED = "product_viewed"
    CART_UPDATED = "cart_updated"
    CHECKOUT_STARTED = "checkout_started"
    PAYMENT_PROCESSED = "payment_processed"
    ORDER_COMPLETED = "order_completed"
    ERROR = "error"

class Analytics:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configura logger para eventos
        self.event_logger = logging.getLogger("events")
        self.event_logger.setLevel(logging.INFO)
        
        # Handler para arquivo de eventos
        events_file = self.log_dir / "events.log"
        event_handler = logging.FileHandler(events_file)
        event_handler.setFormatter(
            logging.Formatter('%(asctime)s\t%(message)s')
        )
        self.event_logger.addHandler(event_handler)
        
        # Configura logger para erros
        self.error_logger = logging.getLogger("errors")
        self.error_logger.setLevel(logging.ERROR)
        
        # Handler para arquivo de erros
        errors_file = self.log_dir / "errors.log"
        error_handler = logging.FileHandler(errors_file)
        error_handler.setFormatter(
            logging.Formatter('%(asctime)s\t%(levelname)s\t%(message)s')
        )
        self.error_logger.addHandler(error_handler)
    
    def track_event(
        self,
        event_type: EventType,
        user_id: str,
        data: Optional[Dict[str, Any]] = None,
        channel: Optional[str] = None
    ) -> None:
        """
        Registra um evento no sistema
        """
        event = {
            "event_type": event_type.value,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "channel": channel,
            "data": data or {}
        }
        
        self.event_logger.info(json.dumps(event))
    
    def track_error(
        self,
        error: Exception,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra um erro no sistema
        """
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        
        self.error_logger.error(json.dumps(error_data))

class MetricsCollector:
    def __init__(self):
        self.metrics: Dict[str, Dict[str, int]] = {
            "messages": {"total": 0, "by_channel": {}},
            "products": {"viewed": 0, "added_to_cart": 0},
            "orders": {"started": 0, "completed": 0},
            "errors": {"total": 0, "by_type": {}}
        }
    
    def increment_metric(
        self,
        category: str,
        metric: str,
        value: int = 1,
        subcategory: Optional[str] = None
    ) -> None:
        """
        Incrementa uma métrica específica
        """
        if category in self.metrics:
            if subcategory:
                if subcategory not in self.metrics[category]:
                    self.metrics[category][subcategory] = 0
                self.metrics[category][subcategory] += value
            else:
                self.metrics[category][metric] += value
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna todas as métricas coletadas
        """
        return self.metrics

class AnalyticsManager:
    def __init__(self):
        self.analytics = Analytics()
        self.metrics = MetricsCollector()
    
    def track_message(
        self,
        user_id: str,
        message: str,
        channel: str,
        is_incoming: bool
    ) -> None:
        """
        Registra uma mensagem enviada ou recebida
        """
        event_type = (
            EventType.MESSAGE_RECEIVED if is_incoming
            else EventType.MESSAGE_SENT
        )
        
        self.analytics.track_event(
            event_type,
            user_id,
            {"message": message},
            channel
        )
        
        self.metrics.increment_metric("messages", "total")
        self.metrics.increment_metric(
            "messages",
            "by_channel",
            subcategory=channel
        )
    
    def track_product_view(
        self,
        user_id: str,
        product_id: str,
        channel: str
    ) -> None:
        """
        Registra visualização de produto
        """
        self.analytics.track_event(
            EventType.PRODUCT_VIEWED,
            user_id,
            {"product_id": product_id},
            channel
        )
        
        self.metrics.increment_metric("products", "viewed")
    
    def track_cart_update(
        self,
        user_id: str,
        cart_data: Dict[str, Any],
        channel: str
    ) -> None:
        """
        Registra atualização no carrinho
        """
        self.analytics.track_event(
            EventType.CART_UPDATED,
            user_id,
            cart_data,
            channel
        )
        
        self.metrics.increment_metric(
            "products",
            "added_to_cart",
            value=len(cart_data.get("items", []))
        )
    
    def track_checkout(
        self,
        user_id: str,
        order_id: str,
        total: float,
        channel: str
    ) -> None:
        """
        Registra início de checkout
        """
        self.analytics.track_event(
            EventType.CHECKOUT_STARTED,
            user_id,
            {
                "order_id": order_id,
                "total": total
            },
            channel
        )
        
        self.metrics.increment_metric("orders", "started")
    
    def track_order_completion(
        self,
        user_id: str,
        order_id: str,
        total: float,
        channel: str
    ) -> None:
        """
        Registra conclusão de pedido
        """
        self.analytics.track_event(
            EventType.ORDER_COMPLETED,
            user_id,
            {
                "order_id": order_id,
                "total": total
            },
            channel
        )
        
        self.metrics.increment_metric("orders", "completed")
    
    def track_error(
        self,
        error: Exception,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Registra um erro
        """
        self.analytics.track_error(error, user_id, context)
        
        error_type = type(error).__name__
        self.metrics.increment_metric("errors", "total")
        self.metrics.increment_metric(
            "errors",
            "by_type",
            subcategory=error_type
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Retorna todas as métricas coletadas
        """
        return self.metrics.get_metrics()
