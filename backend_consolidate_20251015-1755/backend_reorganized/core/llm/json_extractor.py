import json, re
from typing import Any, Dict

def extract_json(payload: str) -> Dict[str, Any]:
    """Robust JSON extractor from LLM output."""
    if not payload:
        return {}
    # Try fenced block
    m = re.search(r"```json\\s*(.*?)\\s*```", payload, re.DOTALL | re.IGNORECASE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    # Try first { ... } last }
    try:
        start, end = payload.find("{"), payload.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(payload[start:end])
    except Exception:
        pass
    return {"raw_response": payload[:1000]}
