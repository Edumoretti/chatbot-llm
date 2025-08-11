from typing import Optional, Dict, Any, List
import aiohttp
from src.config import CATALOG_API_URL, CATALOG_API_KEY

class CatalogAPI:
    def __init__(self):
        self.base_url = "https://api-genove.agcodecraft.com/api/public"
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    async def get_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca informações de um produto específico
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/products/{product_id}",
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                return None
    
    async def search_products(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca produtos por termo de pesquisa na API Genove
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/products",
                params={'text': query},
                headers=self.headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('data', [])
                return []
    
    async def get_brands_and_categories(self) -> Dict[str, Any]:
        """
        Busca marcas e categorias disponíveis
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/start",
                params={'lang': 'pt', 'tem_estoque': '1'},
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {}
    
    async def get_brands(self) -> List[Dict[str, Any]]:
        """
        Retorna apenas as marcas disponíveis
        """
        data = await self.get_brands_and_categories()
        return data.get('brands', [])
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """
        Retorna apenas as categorias disponíveis
        """
        data = await self.get_brands_and_categories()
        return data.get('categories', [])
