from typing import Dict, Any
import discord
from discord.ext import commands
from .webhook_utils import BaseWebhook, WebhookError
from src.config import DISCORD_TOKEN

class DiscordWebhook(commands.Bot):
    def __init__(self, orchestrator, shopping_cart, catalog_api, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents
        )
        
        self.orchestrator = orchestrator
        self.shopping_cart = shopping_cart
        self.catalog_api = catalog_api
        
        # Registra comandos
        self.add_commands()
    
    def add_commands(self):
        @self.command(name='produto')
        async def search_product(ctx, *, query: str):
            """Busca produtos no catálogo"""
            print(f"🔍 Buscando produtos para: {query}")
            
            # Busca produtos diretamente no catálogo
            products = await self.catalog_api.search_products(query)
            print(f"📦 Encontrados {len(products)} produtos")
            
            if not products:
                await ctx.send(f"❌ Nenhum produto encontrado para '{query}'")
                return
            
            # Mostra até 5 produtos
            for product in products[:5]:
                embed = discord.Embed(
                    title=product.get('titulo', 'Produto'),
                    description=f"Marca: {product.get('marca', 'N/A')}",
                    color=discord.Color.blue()
                )
                
                # Preço com símbolo da moeda
                moeda = product.get('moeda', {})
                simbolo = moeda.get('simbolo', 'R$')
                preco = product.get('valor_venda', '0')
                embed.add_field(name="Preço", value=f"{simbolo} {preco}", inline=True)
                
                # Código do produto
                if product.get('codigo'):
                    embed.add_field(name="Código", value=product['codigo'], inline=True)
                
                # Imagem do produto
                imagens = product.get('imagens', [])
                if imagens and len(imagens) > 0:
                    embed.set_thumbnail(url=imagens[0]['url'])
                
                await ctx.send(embed=embed)
        
        @self.command(name='marcas')
        async def list_brands(ctx):
            """Lista marcas disponíveis"""
            brands = await self.catalog_api.get_brands()
            
            if not brands:
                await ctx.send("❌ Nenhuma marca encontrada")
                return
            
            # Mostra até 10 marcas
            brand_list = "\n".join([f"- {brand['nome']}" for brand in brands[:10]])
            
            embed = discord.Embed(
                title="Marcas Disponíveis",
                description=brand_list,
                color=discord.Color.green()
            )
            
            if len(brands) > 10:
                embed.set_footer(text=f"E mais {len(brands) - 10} marcas...")
            
            await ctx.send(embed=embed)
        
        @self.command(name='categorias')
        async def list_categories(ctx):
            """Lista categorias disponíveis"""
            categories = await self.catalog_api.get_categories()
            
            if not categories:
                await ctx.send("❌ Nenhuma categoria encontrada")
                return
            
            # Mostra até 10 categorias
            cat_list = "\n".join([f"- {cat['name']}" for cat in categories[:10]])
            
            embed = discord.Embed(
                title="Categorias Disponíveis",
                description=cat_list,
                color=discord.Color.purple()
            )
            
            if len(categories) > 10:
                embed.set_footer(text=f"E mais {len(categories) - 10} categorias...")
            
            await ctx.send(embed=embed)
        
        @self.command(name='chat')
        async def chat_with_bot(ctx, *, message: str):
            """Conversa com o bot usando IA"""
            user_id = str(ctx.author.id)
            
            # Usa o orquestrador com roteamento inteligente
            response = await self.orchestrator.process_message(
                user_id=user_id,
                message=message,
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
