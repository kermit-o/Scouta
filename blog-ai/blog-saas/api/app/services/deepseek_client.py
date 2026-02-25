# app/services/deepseek_client.py
import warnings
warnings.warn("⚠️ deepseek_client.py está obsoleto, usando LLMClient en su lugar")

import time
import os
import requests
from typing import Any
from app.services.llm_client import LLMClient

class DeepSeekClient:
    def __init__(self) -> None:
        self._llm = LLMClient()
        # Forzar uso de DeepSeek como fallback para mantener compatibilidad
        self._llm.use_qwen = False
        self.api_key = self._llm.deepseek_api_key
        self.base_url = self._llm.deepseek_base_url
        self.model = self._llm.deepseek_model
        self.max_tokens = self._llm.deepseek_max_tokens
        self.temperature = self._llm.deepseek_temperature
        self.timeout = self._llm.timeout

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def chat(self, system: str, user: str) -> str:
        return self._llm._chat_deepseek(system, user)

    def score_text(self, text: str) -> tuple[int, str]:
        from app.services.moderation_scorer_patch import score_text_with_llm
        result = score_text_with_llm(text)
        return result.score, result.reason
