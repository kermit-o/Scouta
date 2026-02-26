from dataclasses import dataclass
from app.services.deepseek_client import DeepSeekClient
from app.services.llm_client import LLMClient
from app.core.config import settings
import re

from app.services.deepseek_client import DeepSeekClient
import json

@dataclass(frozen=True)
class ModerationResult:
    score: int
    reason: str

def score_text_with_deepseek(text: str) -> ModerationResult:
    """
    Risk score: 0..100 (higher = riskier).
    Returns ModerationResult(score:int, reason:str)
    """
    ds = LLMClient()
    #ds = DeepSeekClient()
    if not ds.is_enabled():
        return ModerationResult(score=0, reason="llm_off")

    system = (
        'Return ONLY JSON: {"score":0-100,"reason":"short"}. '
        "Score 0=safe, 100=reject. Consider harassment/hate/threats/sexual/self-harm/illegal/spam."
    )
    user = f"TEXT:\n{text}\n\nReturn JSON only."

    out = ds.chat(system=system, user=user)

    try:
        data = json.loads(out)
    except Exception:
        m = re.search(r"\{.*\}", out, re.DOTALL)
        if not m:
            return ModerationResult(score=50, reason="parse_fail")
        data = json.loads(m.group(0))

    raw_score = data.get("score", 0)
    reason = (data.get("reason") or "deepseek").strip()

    # Handle null/None or weird types safely
    if raw_score is None:
        score = 50
        reason = "score_null"
    else:
        try:
            score = int(raw_score)
        except Exception:
            # try extracting digits from string
            m = re.search(r"\b(\d{1,3})\b", str(raw_score))
            score = int(m.group(1)) if m else 50
            reason = "score_parse"

    # clamp 0..100
    if score < 0:
        score = 0
    elif score > 100:
        score = 100

    return ModerationResult(score=score, reason=reason)