# app/services/moderation_scorer_patch.py
from app.services.llm_client import LLMClient
from typing import NamedTuple

class ModScore(NamedTuple):
    score: int
    reason: str

_llm = LLMClient()

def score_text_with_llm(text: str) -> ModScore:
    """Versión unificada de moderación usando LLMClient"""
    system_prompt = """You are a content moderation system. 
    Score the following text from 0-100 where:
    - 0-30: Dangerous/violent/hateful
    - 31-60: Neutral/acceptable  
    - 61-100: Positive/constructive
    
    Return ONLY a JSON: {"score": number, "reason": "brief explanation"}"""
    
    try:
        response = _llm.chat(system_prompt, text)
        import json
        result = json.loads(response.strip())
        return ModScore(result.get("score", 50), result.get("reason", "no_reason"))
    except Exception as e:
        return ModScore(50, f"scoring_error: {str(e)[:50]}")
