from __future__ import annotations

import os
import json
from typing import List, Dict, Any, Optional
import httpx


class DeepSeekClient:
    """
    Very small wrapper around DeepSeek Chat Completions API.
    Expects DEEPSEEK_API_KEY in environment.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.deepseek.com"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set in environment.")
        self.base_url = base_url.rstrip("/")

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "deepseek-chat",
        temperature: float = 0.2,
        max_tokens: int = 2048,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Calls DeepSeek chat completions and returns assistant content string."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        url = f"{self.base_url}/chat/completions"
        with httpx.Client(timeout=60) as client:
            r = client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()

        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            raise RuntimeError(f"Unexpected DeepSeek response: {json.dumps(data)[:800]}")


# --- Stub para el builder LLM ---
def generate(prompt: str, system: Optional[str] = None, **kwargs) -> str:
    """
    Stub seguro para el builder.
    - Si falta DEEPSEEK_API_KEY -> RuntimeError claro.
    - Si existe, devuelve texto simple sin llamada real a API.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is not set")

    header = f"[SYSTEM]: {system}\n" if system else ""
    return header + f"[DEEPSEEK_STUB_RESPONSE] {prompt[:256]}"
