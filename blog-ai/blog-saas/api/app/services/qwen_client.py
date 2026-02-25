# app/services/qwen_client.py
import warnings
warnings.warn("⚠️ qwen_client.py está obsoleto, usando LLMClient en su lugar")

import time
import os
import requests
from typing import Any
from app.services.llm_client import LLMClient

class QwenClient:
    def __init__(self) -> None:
        self._llm = LLMClient()
        # Forzar uso de Qwen
        self._llm.use_qwen = True
        self.api_key = self._llm.qwen_api_key
        self.base_url = self._llm.qwen_base_url
        self.model = self._llm.qwen_model
        self.max_tokens = self._llm.qwen_max_tokens
        self.temperature = self._llm.qwen_temperature
        self.timeout = self._llm.timeout

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def chat(self, system: str, user: str) -> str:
        return self._llm._chat_qwen(system, user)
