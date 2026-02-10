# backend/services/twilio_security.py
import os
import logging
from typing import Dict

from fastapi import Request, HTTPException
from twilio.request_validator import RequestValidator

logger = logging.getLogger(__name__)


def _get_public_url(request: Request) -> str:
    """
    Twilio valida la firma con la URL EXACTA que él llama.
    En Codespaces/producción, usa WEBHOOK_BASE_URL para fijar el host público.
    """
    base = os.getenv("WEBHOOK_BASE_URL")
    if base:
        return f"{base.rstrip('/')}{request.url.path}"
    # fallback: usa la URL que FastAPI ve (útil en local)
    return str(request.url)


async def verify_twilio_request(request: Request) -> None:
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    if not auth_token:
        # En dev puedes permitirlo, pero mejor ser explícito:
        logger.warning("TWILIO_AUTH_TOKEN missing: skipping Twilio signature validation")
        return

    form = await request.form()
    params: Dict[str, str] = dict(form)

    validator = RequestValidator(auth_token)
    url = _get_public_url(request)
    signature = request.headers.get("X-Twilio-Signature", "")

    ok = validator.validate(url, params, signature)
    if not ok:
        logger.warning("Invalid Twilio signature. url=%s", url)
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
