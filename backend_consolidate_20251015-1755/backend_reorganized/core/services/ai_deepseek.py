import os, json, requests

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
        if not self.api_key:
            raise RuntimeError("Missing DEEPSEEK_API_KEY")

    def chat_complete(self, prompt: str, model: str = None, temperature: float = 0.2, max_tokens: int = 4096) -> dict:
        model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-coder")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        r = requests.post(self.api_url, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        # Normalizamos a {text: "..."} además del payload crudo
        text = ""
        try:
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "") or ""
        except Exception:
            pass
        return {"raw": data, "text": text}

ds_client = DeepSeekClient()
