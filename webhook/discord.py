from typing import Dict, Any
import discord
from discord.ext import commands
from .webhook_utils import BaseWebhook, WebhookError
from ..config import DISCORD_TOKEN

class DiscordWebhook(BaseWebhook, commands.Bot):
    def __init__(self, *args, **kwargs):
        BaseWebhook.__init__(self, *args)
        commands.Bot.__init__(
            self,
            command_prefix='!',
            intents=discord.Intents.default()
        )
        
        # Registra comandos
        self.add_commands()
    
    def add_commands(self):
        @self.command(name='produto')
        async def search_product(ctx, *, query: str):
            """Busca produtos no catálogo"""
            user_id = str(ctx.author.id)
            response = await self.orchestrator.process_message(
                user_id=user_id,
                message=f"buscar produto {query}",
                channel='discord'
            )
            await ctx.send(response)
        
        @self.command(name='carrinho')
        async def view_cart(ctx):
            """Mostra o carrinho atual"""
            user_id = str(ctx.author.id)
            cart = self.shopping_cart.get_cart_summary(user_id)
            
            if not cart['items']:
                await ctx.send("Seu carrinho está vazio!")
                return
            
            embed = discord.Embed(
                title="Seu Carrinho",
                color=discord.Color.blue()
            )
            
            for item in cart['items']:
                embed.add_field(
                    name=item['name'],
                    value=f"Quantidade: {item['quantity']}\nPreço: R$ {item['price']}",
                    inline=False
                )
            
            embed.add_field(
                name="Total",
                value=f"R$ {cart['total']}",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    async def handle_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa mensagens do Discord
        """
        # As mensagens são processadas pelos comandos registrados
        return {'status': 'success'}
    
    async def send_message(
        self,
        user_id: str,
        message: str,
        **kwargs
    ) -> bool:
        """
        Envia mensagem para usuário no Discord
        """
        try:
            user = await self.fetch_user(int(user_id))
            await user.send(message)
            return True
        except Exception as e:
            raise WebhookError(f"Erro ao enviar mensagem no Discord: {str(e)}")
    
    async def send_product_card(
        self,
        user_id: str,
        product: Dict[str, Any]
    ) -> bool:
        """
        Envia card de produto com imagem e botões
        """
        try:
            user = await self.fetch_user(int(user_id))
            
            embed = discord.Embed(
                title=product['name'],
                description=product['description'],
                color=discord.Color.green()
            )
            
            embed.set_image(url=product['image_url'])
            embed.add_field(
                name="Preço",
                value=f"R$ {product['price']}",
                inline=False
            )
            
            # Adiciona botão de ação
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    label="Adicionar ao Carrinho",
                    style=discord.ButtonStyle.primary,
                    custom_id=f"add_to_cart_{product['id']}"
                )
            )
            
            await user.send(embed=embed, view=view)
            return True
            
        except Exception as e:
            raise WebhookError(f"Erro ao enviar card de produto no Discord: {str(e)}")
