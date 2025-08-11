from typing import Dict, Any
from enum import Enum
from openai import OpenAI
from src.config import OPENAI_API_KEY

class IntentType(Enum):
    FAQ = "faq"
    PRODUCT_SEARCH = "product_search"
    GENERAL = "general"

class IntentDetector:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def detect_intent(self, message: str) -> IntentType:
        """
        Detecta intenção usando OpenAI
        """
        try:
            return self._detect_with_openai(message)
        except:
            # Fallback para detecção simples
            return self._simple_detection(message)
    
    def extract_search_term(self, message: str) -> str:
        """
        Extrai apenas o termo de busca da mensagem usando IA
        """
        try:
            return self._extract_with_openai(message)
        except:
            return self._simple_extract(message)
    
    def _extract_with_openai(self, message: str) -> str:
        """Usa OpenAI para extrair termo de busca"""
        prompt = f"""Extraia APENAS o nome da marca ou produto que o usuário quer buscar.

Exemplos:
- "ola, quero comprar um perfume da marca lattafa" → lattafa
- "quero comprar um perfume lattafa" → lattafa
- "liste todos os perfumes armaf" → armaf
- "preciso de um celular xiaomi" → xiaomi
- "mostrar produtos apple" → apple
- "buscar notebook" → notebook
- "perfumes da marca chanel" → chanel

Mensagem: "{message}"

Responda APENAS com o termo de busca (marca ou produto):"""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=20
        )
        
        result = response.choices[0].message.content.strip().lower()
        print(f"Termo extraído pela IA: '{result}'")
        return result
    
    def _simple_extract(self, message: str) -> str:
        """Extração simples como fallback"""
        message_lower = message.lower()
        
        # Marcas conhecidas (busca mais ampla)
        brands = ['lattafa', 'armaf', 'xiaomi', 'apple', 'samsung', 'afnan', 'chanel', 'gucci', 'dior']
        for brand in brands:
            if brand in message_lower:
                print(f"Marca encontrada no fallback: {brand}")
                return brand
        
        # Produtos genéricos
        if 'perfume' in message_lower:
            return 'perfume'
        elif 'celular' in message_lower:
            return 'celular'
        
        return 'perfume'
    
    def _detect_with_openai(self, message: str) -> IntentType:
        """Usa OpenAI para detectar intenção"""
        prompt = f"""Classifique esta mensagem em UMA das categorias:

FAQ: perguntas sobre horário, funcionamento, entrega, pagamento, suporte, garantia, troca
PRODUCT_SEARCH: busca/lista de produtos, marcas, preços, compras, estoque
GENERAL: outras perguntas gerais

Mensagem: "{message}"

Responda APENAS: FAQ, PRODUCT_SEARCH ou GENERAL"""
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().upper()
        
        if "PRODUCT_SEARCH" in result:
            return IntentType.PRODUCT_SEARCH
        elif "FAQ" in result:
            return IntentType.FAQ
        else:
            return IntentType.GENERAL
    
    def _simple_detection(self, message: str) -> IntentType:
        """Fallback simples se Ollama não estiver disponível"""
        message_lower = message.lower()
        
        # Palavras-chave de produto
        product_words = ["produto", "comprar", "perfume", "celular", "lattafa", "armaf", "liste", "mostrar"]
        if any(word in message_lower for word in product_words):
            return IntentType.PRODUCT_SEARCH
        
        # Palavras-chave de FAQ
        faq_words = ["horario", "entrega", "pagamento", "como", "quando", "onde"]
        if any(word in message_lower for word in faq_words):
            return IntentType.FAQ
        
        return IntentType.GENERAL