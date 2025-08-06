from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class ContextManager:
    def __init__(self):
        self.contexts: Dict[str, Dict[str, Any]] = {}
        self.expiration_time = timedelta(minutes=30)
    
    def set_context(self, user_id: str, context_data: Dict[str, Any]) -> None:
        """
        Define o contexto para um usuário específico
        
        Args:
            user_id: Identificador único do usuário
            context_data: Dados do contexto a serem armazenados
        """
        self.contexts[user_id] = {
            'data': context_data,
            'timestamp': datetime.now()
        }
    
    def get_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera o contexto de um usuário específico
        
        Args:
            user_id: Identificador único do usuário
        
        Returns:
            Dados do contexto ou None se não existir ou estiver expirado
        """
        if user_id not in self.contexts:
            return None
            
        context = self.contexts[user_id]
        if datetime.now() - context['timestamp'] > self.expiration_time:
            del self.contexts[user_id]
            return None
            
        return context['data']
    
    def update_context(self, user_id: str, update_data: Dict[str, Any]) -> None:
        """
        Atualiza o contexto existente de um usuário
        
        Args:
            user_id: Identificador único do usuário
            update_data: Novos dados a serem mesclados com o contexto existente
        """
        current_context = self.get_context(user_id) or {}
        current_context.update(update_data)
        self.set_context(user_id, current_context)
    
    def clear_context(self, user_id: str) -> None:
        """
        Remove o contexto de um usuário específico
        
        Args:
            user_id: Identificador único do usuário
        """
        if user_id in self.contexts:
            del self.contexts[user_id]
