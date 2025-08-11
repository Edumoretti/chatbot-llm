from typing import Dict, Any, Optional
from openai import OpenAI
from .intent_detector import IntentDetector, IntentType
from ..faq.faq_vector_store import FAQVectorStore
from ..catalog.catalog_api import CatalogAPI
from ..config import OPENAI_API_KEY, OPENAI_MODEL

class DialogOrchestrator:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.intent_detector = IntentDetector()
        self.faq_store = FAQVectorStore()
        self.catalog_api = CatalogAPI()
        
    async def process_message(
        self,
        user_id: str,
        message: str,
        channel: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Processa mensagem com roteamento inteligente
        """
        try:
            # Detecta intenção
            intent = self.intent_detector.detect_intent(message)
            print(f"Intent detectado: {intent.value}")
            
            # Rota 1: FAQ - Banco Vetorial
            if intent == IntentType.FAQ:
                faq_response = self.faq_store.search_faq(message)
                if faq_response:
                    return faq_response
                # Se não encontrar FAQ, vai para rota geral
            
            # Rota 2: Catálogo de Produtos
            elif intent == IntentType.PRODUCT_SEARCH:
                return await self._handle_product_search(message)
            
            # Rota 3: Perguntas Gerais
            return await self._handle_general_question(message, user_id)
            
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")
            return "Desculpe, ocorreu um erro. Tente novamente."
    
    async def _handle_product_search(self, message: str) -> str:
        """Rota 2: Busca produtos e formata resposta"""
        # Extrai termo de busca usando IA
        search_term = self.intent_detector.extract_search_term(message)
        print(f"Termo extraído: '{search_term}' da mensagem: '{message}'")
        
        # Busca produtos
        products = await self.catalog_api.search_products(search_term)
        print(f"Produtos encontrados: {len(products)}")
        
        if not products:
            return f"Não encontrei produtos para '{search_term}'. Tente outro termo."
        
        # Formata resposta com LLM
        products_text = "\n".join([
            f"- {p.get('titulo', 'N/A')} - {p.get('moeda', {}).get('simbolo', 'R$')} {p.get('valor_venda', '0')}"
            for p in products[:5]
        ])
        
        prompt = f"""Você é um assistente de vendas. Apresente estes produtos de forma atrativa:

{products_text}

Responda de forma profissional e incentive a compra."""
        
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def _handle_general_question(self, message: str, user_id: str) -> str:
        """Rota 3: Perguntas gerais com GPT"""
        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": message}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    

    
    def clear_conversation(self, user_id: str) -> None:
        """Limpa conversa (mantido para compatibilidade)"""
        pass
