from pathlib import Path
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configurações básicas
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações da API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')

# Configurações do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dados/db.sqlite')

# Configurações dos webhooks
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Configurações da API de produtos
CATALOG_API_URL = os.getenv('CATALOG_API_URL')
CATALOG_API_KEY = os.getenv('CATALOG_API_KEY')

# Configurações do servidor
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

PAYMENT_GATEWAY_URL = os.getenv('PAYMENT_GATEWAY_URL')
PAYMENT_GATEWAY_KEY = os.getenv('PAYMENT_GATEWAY_KEY')

# Configurações do WhatsApp
WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL')
WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY')
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')

# Configurações do Discord
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
