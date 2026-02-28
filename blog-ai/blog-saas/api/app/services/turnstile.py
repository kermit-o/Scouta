import os
import requests

TURNSTILE_SECRET = os.getenv("TURNSTILE_SECRET_KEY", "")

def verify_turnstile(token: str, ip: str = "") -> bool:
    """Verifica el token de Cloudflare Turnstile"""
    if not TURNSTILE_SECRET:
        return True  # Si no hay secret key configurada, permitir
    if not token:
        return False
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
        print(f"⚠️ Turnstile verify error: {e}")
        return True  # En caso de error, no bloquear
