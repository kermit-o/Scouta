# app/services/llm_client.py
import time
import os
import requests
from typing import Any, Optional, Dict
import json

class LLMClient:
    """Cliente unificado que intenta Qwen primero y DeepSeek como fallback"""
    
    def __init__(self):
        # Configuración Qwen
        self.qwen_api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("QWEN_API_KEY", "").strip()
        self.qwen_base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1").rstrip("/")
        self.qwen_model = os.getenv("DASHSCOPE_MODEL", "qwen-plus").strip()
        self.qwen_max_tokens = int(os.getenv("DASHSCOPE_MAX_TOKENS", "2048"))
        self.qwen_temperature = float(os.getenv("DASHSCOPE_TEMPERATURE", "0.7"))
        
        # Configuración DeepSeek (fallback)
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
        self.deepseek_max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "350"))
        self.deepseek_temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.6"))
        
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        self.last_error = None
        self.use_qwen = True  # Intentar Qwen primero

    def is_enabled(self) -> bool:
        """Verifica si al menos un cliente está configurado"""
        return bool(self.qwen_api_key) or bool(self.deepseek_api_key)

    def chat(self, system: str, user: str) -> str:
        """Intenta Qwen, si falla usa DeepSeek"""
        
        # Intentar Qwen primero
        if self.use_qwen and self.qwen_api_key:
            try:
                print("🔵 Intentando con Qwen...")
                return self._chat_qwen(system, user)
            except Exception as e:
                print(f"⚠️ Qwen falló: {e}")
                self.last_error = e
                # Si Qwen falla, cambiar a DeepSeek para futuras llamadas
                self.use_qwen = False
        
        # Fallback a DeepSeek
        if self.deepseek_api_key:
            print("🟢 Usando DeepSeek como fallback...")
            return self._chat_deepseek(system, user)
        
        raise RuntimeError("No LLM clients available (Qwen and DeepSeek both disabled)")

    def _chat_qwen(self, system: str, user: str) -> str:
        """Llamada específica a Qwen"""
        url = f"{self.qwen_base_url}/chat/completions"
        payload = {
            "model": self.qwen_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.qwen_temperature,
            "max_tokens": self.qwen_max_tokens,
            "stream": False,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.qwen_api_key}",
        }

        for attempt in range(3):
            try:
                r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                r.raise_for_status()
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
            except requests.Timeout:
                if attempt == 2:
                    raise
                time.sleep(2 * (attempt + 1))
            except requests.RequestException as e:
                if attempt == 2:
                    raise
                time.sleep(1)
        
        raise RuntimeError("Qwen API failed after retries")

    def _chat_deepseek(self, system: str, user: str) -> str:
        """Llamada específica a DeepSeek"""
        url = f"{self.deepseek_base_url}/chat/completions"
        payload = {
            "model": self.deepseek_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.deepseek_temperature,
            "max_tokens": self.deepseek_max_tokens,
            "stream": False,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.deepseek_api_key}",
        }

        for attempt in range(3):
            try:
                r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                r.raise_for_status()
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
            except requests.Timeout:
                if attempt == 2:
                    raise
                time.sleep(1.5 * (attempt + 1))
        
        raise RuntimeError("DeepSeek API failed after retries")
