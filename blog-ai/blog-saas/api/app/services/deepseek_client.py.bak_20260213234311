import os
import requests
from typing import Any

class DeepSeekClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat").strip()
        self.max_tokens = int(os.getenv("DEEPSEEK_MAX_TOKENS", "350"))
        self.temperature = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.6"))
        self.timeout = int(os.getenv("DEEPSEEK_TIMEOUT", "20"))

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def chat(self, system: str, user: str) -> str:
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set")

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

        r = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()

        # DeepSeek follows OpenAI-like shape: choices[0].message.content :contentReference[oaicite:6]{index=6}
        return data["choices"][0]["message"]["content"].strip()

    def score_text(self, text: str) -> tuple[int, str]:
        """
        Score text for moderation (0-100).
        Returns: (score, reason)
        """
        if not self.api_key:
            return 50, "api_key_not_set"
        
        system_prompt = """You are a content moderation system. 
        Score the following text from 0-100 where:
        - 0-30: Dangerous/violent/hateful
        - 31-60: Neutral/acceptable  
        - 61-100: Positive/constructive
        
        Return ONLY a JSON: {"score": number, "reason": "brief explanation"}"""
        
        try:
            response = self.chat(system_prompt, text)
            import json
            result = json.loads(response.strip())
            return result.get("score", 50), result.get("reason", "no_reason")
        except Exception as e:
            return 50, f"scoring_error: {str(e)[:50]}"
