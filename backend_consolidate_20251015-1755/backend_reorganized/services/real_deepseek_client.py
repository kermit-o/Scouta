"""
FixedDeepSeekClient - Cliente compatible con el sistema existente
"""
import os
from typing import Dict, Any, Optional
import aiohttp
import json

class FixedDeepSeekClient:
    """Cliente DeepSeek compatible con los agentes existentes"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def generate_response(self, prompt: str, max_tokens: int = 4000) -> str:
        """Genera respuesta usando DeepSeek API"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-coder",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/completions", 
                headers=headers, 
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    return f"Error: {response.status} - {error_text}"
                    
        except Exception as e:
            return f"Exception: {str(e)}"
    
    async def close(self):
        """Cierra la sesión"""
        if self.session:
            await self.session.close()
            self.session = None

# También proveer el alias para compatibilidad
FixedDeepSeekClient = FixedDeepSeekClient
