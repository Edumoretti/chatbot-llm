from typing import Dict, Any, Optional
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from ..config import OPENAI_API_KEY, OPENAI_MODEL

class DialogOrchestrator:
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model_name=OPENAI_MODEL,
            temperature=0.7
        )
        self.conversations: Dict[str, ConversationChain] = {}
        
    def get_or_create_conversation(self, user_id: str) -> ConversationChain:
        """
        Obtém ou cria uma nova conversa para um usuário específico
        """
        if user_id not in self.conversations:
            memory = ConversationBufferMemory()
            self.conversations[user_id] = ConversationChain(
                llm=self.llm,
                memory=memory,
                verbose=True
            )
        return self.conversations[user_id]
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        channel: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Processa uma mensagem do usuário e retorna uma resposta apropriada
        
        Args:
            user_id: Identificador único do usuário
            message: Mensagem do usuário
            channel: Canal de origem da mensagem (whatsapp, discord, etc)
            context: Contexto adicional da conversa (opcional)
        
        Returns:
            Resposta processada para o usuário
        """
        conversation = self.get_or_create_conversation(user_id)
        
        # Adiciona contexto à mensagem se disponível
        if context:
            message = f"Contexto: {context}\nMensagem: {message}"
            
        try:
            response = await conversation.arun(input=message)
            return response
        except Exception as e:
            # Log do erro e retorna uma mensagem amigável
            print(f"Erro ao processar mensagem: {e}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente."

    def clear_conversation(self, user_id: str) -> None:
        """
        Limpa o histórico de conversa de um usuário específico
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
