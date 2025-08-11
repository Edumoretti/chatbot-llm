#!/usr/bin/env python3
"""
Script para iniciar o bot do Discord
"""
import asyncio
from webhook.discord import DiscordWebhook
from src.orchestrator.orchestrator import DialogOrchestrator
from src.cart.cart import ShoppingCart
from src.catalog.catalog_api import CatalogAPI
from src.config import DISCORD_TOKEN

async def main():
    if not DISCORD_TOKEN:
        print("❌ DISCORD_TOKEN não configurado no arquivo .env")
        return
    
    # Inicializa serviços
    catalog_api = CatalogAPI()
    orchestrator = DialogOrchestrator()
    shopping_cart = ShoppingCart(catalog_api)
    
    # Cria bot do Discord
    bot = DiscordWebhook(
        orchestrator=orchestrator,
        shopping_cart=shopping_cart,
        catalog_api=catalog_api
    )
    
    print("🤖 Iniciando bot do Discord...")
    print("📝 Comandos disponíveis:")
    print("   !chat <mensagem> - Conversar com IA")
    print("   !produto <nome> - Buscar produtos")
    print("   !marcas - Listar marcas")
    print("   !categorias - Listar categorias")
    print("   !carrinho - Ver carrinho")
    
    try:
        await bot.start(DISCORD_TOKEN)
    except Exception as e:
        print(f"❌ Erro ao iniciar bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())