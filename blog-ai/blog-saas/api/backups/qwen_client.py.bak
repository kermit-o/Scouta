import time
import os
import requests
from typing import Any

class QwenClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
        self.base_url = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1").rstrip("/")
        self.model = os.getenv("DASHSCOPE_MODEL", "qwen3.5-plus").strip()
        self.max_tokens = int(os.getenv("DASHSCOPE_MAX_TOKENS", "512"))
        self.temperature = float(os.getenv("DASHSCOPE_TEMPERATURE", "0.7"))
        self.timeout = int(os.getenv("DASHSCOPE_TIMEOUT", "30"))

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def chat(self, system: str, user: str) -> str:
        if not self.api_key:
            raise RuntimeError("DASHSCOPE_API_KEY not set")

        url = f"{self.base_url}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": False,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            for attempt in range(3):
                try:
                    r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                    r.raise_for_status()
                    break
                except requests.Timeout:
                    if attempt == 2:
                        raise
                    time.sleep(2 * (attempt + 1))
                except requests.RequestException as e:
                    if attempt == 2:
                        raise
                    time.sleep(1)
        except Exception as e:
            raise RuntimeError(f"Qwen API error: {str(e)}")

        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
