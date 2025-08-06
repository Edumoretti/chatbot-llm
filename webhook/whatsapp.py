from typing import Dict, Any
import aiohttp
from .webhook_utils import BaseWebhook, WebhookError
from ..config import (
    WHATSAPP_API_URL,
    WHATSAPP_API_KEY,
    WHATSAPP_VERIFY_TOKEN
)

class WhatsAppWebhook(BaseWebhook):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_url = WHATSAPP_API_URL
        self.api_key = WHATSAPP_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    async def handle_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa webhooks do WhatsApp
        """
        try:
            # Verifica se é uma mensagem de texto
            if 'messages' in data and data['messages']:
                message = data['messages'][0]
                if message.get('type') == 'text':
                    user_id = message['from']
                    text = message['text']['body']
                    
                    # Processa a mensagem através do orquestrador
                    response = await self.orchestrator.process_message(
                        user_id=user_id,
                        message=text,
                        channel='whatsapp'
                    )
                    
                    # Envia resposta
                    await self.send_message(user_id, response)
                    
                    return {'status': 'success'}
            
            return {'status': 'ignored'}
            
        except Exception as e:
            raise WebhookError(f"Erro ao processar mensagem do WhatsApp: {str(e)}")
    
    async def send_message(
        self,
        user_id: str,
        message: str,
        **kwargs
    ) -> bool:
        """
        Envia mensagem para usuário no WhatsApp
        """
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': user_id,
            'type': 'text',
            'text': {'body': message}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/messages",
                json=payload,
                headers=self.headers
            ) as response:
                return response.status == 200
    
    async def send_product_card(
        self,
        user_id: str,
        product: Dict[str, Any]
    ) -> bool:
        """
        Envia card de produto com imagem e botões
        """
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': user_id,
            'type': 'template',
            'template': {
                'name': 'product_card',
                'language': {'code': 'pt_BR'},
                'components': [
                    {
                        'type': 'header',
                        'parameters': [
                            {
                                'type': 'image',
                                'image': {'link': product['image_url']}
                            }
                        ]
                    },
                    {
                        'type': 'body',
                        'parameters': [
                            {'type': 'text', 'text': product['name']},
                            {'type': 'text', 'text': f"R$ {product['price']}"},
                            {'type': 'text', 'text': product['description']}
                        ]
                    },
                    {
                        'type': 'button',
                        'sub_type': 'quick_reply',
                        'index': 0,
                        'parameters': [{'type': 'text', 'text': 'Adicionar ao Carrinho'}]
                    }
                ]
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/messages",
                json=payload,
                headers=self.headers
            ) as response:
                return response.status == 200
