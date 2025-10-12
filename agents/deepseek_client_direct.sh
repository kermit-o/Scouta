# agents/deepseek_client_direct.py
import os
import httpx
import json
from typing import Dict, Any
from dotenv import load_dotenv

# Cargar .env directamente
load_dotenv()

class DeepSeekClientDirect:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        
        print(f"🔧 Cliente Directo - API Key: {'✅' if self.api_key else '❌'}")
    
    def is_available(self):
        return bool(self.api_key and len(self.api_key) > 20)
    
    async def analyze_idea(self, user_idea: str) -> Dict[str, Any]:
        if not self.is_available():
            print("❌ DeepSeek no disponible - usando fallback")
            return self._get_fallback_analysis(user_idea)
            
        # ... (el resto del código igual que tu cliente actual)
        # Copia aquí todo el método analyze_idea de tu cliente actual

# Probar cliente directo
direct_client = DeepSeekClientDirect()