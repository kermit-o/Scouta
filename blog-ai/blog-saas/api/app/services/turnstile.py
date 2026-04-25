import os
import secrets
import requests

TURNSTILE_SECRET = os.getenv("TURNSTILE_SECRET_KEY", "")
MOBILE_BYPASS_TOKEN = os.getenv("MOBILE_BYPASS_TOKEN", secrets.token_urlsafe(32))

def verify_turnstile(token: str, ip: str = "") -> bool:
    """Verifica el token de Cloudflare Turnstile"""
    if not TURNSTILE_SECRET:
        return True
    if not token:
        return False
    if MOBILE_BYPASS_TOKEN and token == MOBILE_BYPASS_TOKEN:
        return True
    try:
        r = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": TURNSTILE_SECRET,
                "response": token,
                "remoteip": ip,
            },
            timeout=5,
        )
        data = r.json()
        return bool(data.get("success"))
    except Exception as e:
        print(f"[turnstile] verify error: {e}")
        return False  # Fail closed - block on error
