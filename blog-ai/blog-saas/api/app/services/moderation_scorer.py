from dataclasses import dataclass
from app.services.deepseek_client import DeepSeekClient

@dataclass(frozen=True)
class ModerationResult:
    score: int
    reason: str

def score_text_with_deepseek(text: str) -> ModerationResult:
    """
    Risk score: 0..100 (higher = riskier).
    """
    ds = DeepSeekClient()
    if not ds.is_enabled():
        return ModerationResult(score=0, reason="llm_off")

    system = (
        "Return ONLY JSON: {\"score\":0-100,\"reason\":\"short\"}. "
        "Score 0=safe, 100=reject. Consider harassment/hate/threats/sexual/self-harm/illegal/spam."
    )
    user = f"TEXT:\n{text}\n\nReturn JSON only."

    out = ds.chat(system=system, user=user)

    import json
    try:
        data = json.loads(out)
        score = int(data.get("score", 0))
        score = max(0, min(100, score))
        reason = str(data.get("reason", "mvp"))[:60]
        return ModerationResult(score=score, reason=reason or "mvp")
    except Exception:
        return ModerationResult(score=50, reason="parse_fail")
