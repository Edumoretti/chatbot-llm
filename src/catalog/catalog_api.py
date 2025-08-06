from typing import Optional, Dict, Any
import aiohttp
from src.config import CATALOG_API_URL, CATALOG_API_KEY

class CatalogAPI:
    def __init__(self):
        self.base_url = CATALOG_API_URL
        self.api_key = CATALOG_API_KEY
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
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
        Busca produtos por termo de pesquisa
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/products/search",
                params={'q': query},
                headers=self.headers
            ) as response:
                if response.status == 200:
                    return await response.json()
                return []
