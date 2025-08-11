from typing import List, Dict, Any, Optional
import faiss
import numpy as np
from openai import OpenAI
from src.config import OPENAI_API_KEY
import json
import os

class FAQVectorStore:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.dimension = 1536  # OpenAI embedding dimension
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.faq_data = []
        self.embeddings_file = "dados/faq_embeddings.json"
        
        # Carrega FAQs existentes
        self._load_faqs()
    
    def _load_faqs(self):
        """Carrega FAQs padrão"""
        default_faqs = [
            {
                "pergunta": "Qual o horário de funcionamento?",
                "resposta": "Funcionamos de segunda a sexta das 8h às 18h, e sábados das 8h às 12h."
            },
            {
                "pergunta": "Como faço para trocar um produto?",
                "resposta": "Você pode trocar produtos em até 7 dias. Entre em contato conosco pelo WhatsApp."
            },
            {
                "pergunta": "Qual o prazo de entrega?",
                "resposta": "O prazo de entrega é de 2 a 5 dias úteis para todo o país."
            },
            {
                "pergunta": "Quais formas de pagamento vocês aceitam?",
                "resposta": "Aceitamos cartão de crédito, débito, PIX e boleto bancário."
            },
            {
                "pergunta": "Como entrar em contato com o suporte?",
                "resposta": "Você pode nos contatar pelo WhatsApp, Discord ou através do nosso site."
            }
        ]
        
        # Se não existir arquivo de embeddings, cria
        if not os.path.exists(self.embeddings_file):
            self._create_embeddings(default_faqs)
        else:
            self._load_embeddings()
    
    def _create_embeddings(self, faqs: List[Dict[str, str]]):
        """Cria embeddings para as FAQs"""
        embeddings = []
        
        for faq in faqs:
            # Cria embedding da pergunta
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=faq["pergunta"]
            )
            embedding = response.data[0].embedding
            embeddings.append(embedding)
            
            self.faq_data.append(faq)
        
        # Adiciona ao índice FAISS
        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_array)  # Normaliza para cosine similarity
        self.index.add(embeddings_array)
        
        # Salva embeddings
        self._save_embeddings(embeddings)
    
    def _save_embeddings(self, embeddings: List[List[float]]):
        """Salva embeddings em arquivo"""
        data = {
            "faqs": self.faq_data,
            "embeddings": embeddings
        }
        
        os.makedirs("dados", exist_ok=True)
        with open(self.embeddings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_embeddings(self):
        """Carrega embeddings do arquivo"""
        with open(self.embeddings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.faq_data = data["faqs"]
        embeddings = data["embeddings"]
        
        # Reconstrói índice FAISS
        embeddings_array = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_array)
        self.index.add(embeddings_array)
    
    def search_faq(self, question: str, threshold: float = 0.7) -> Optional[str]:
        """
        Busca FAQ mais similar à pergunta
        """
        # Cria embedding da pergunta
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=question
        )
        query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
        faiss.normalize_L2(query_embedding)
        
        # Busca no índice
        scores, indices = self.index.search(query_embedding, k=1)
        
        if scores[0][0] >= threshold:
            best_match_idx = indices[0][0]
            return self.faq_data[best_match_idx]["resposta"]
        
        return None