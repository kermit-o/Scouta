from fastapi import APIRouter
import os

router = APIRouter(tags=["debug"])

@router.get("/debug/llm-test")
def test_llm():
    from app.services.llm_client import LLMClient
    llm = LLMClient()
    result = {
        "qwen_key": bool(llm.qwen_api_key),
        "deepseek_key": bool(llm.deepseek_api_key),
        "qwen_model": llm.qwen_model,
        "is_enabled": llm.is_enabled(),
        "env_keys": [k for k in os.environ if any(x in k.lower() for x in ["qwen","deepseek","dashscope"])],
    }
    if llm.is_enabled():
        try:
            out = llm.chat(system="You are a test.", user="Say OK.")
            result["llm_response"] = out[:100]
            result["status"] = "ok"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
    else:
        result["status"] = "disabled"
    return result
