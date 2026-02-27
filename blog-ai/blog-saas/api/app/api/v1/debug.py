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
            out = llm.chat(system="You are an expert writer.", user="Write a 200 word essay about AI creativity.")
            result["llm_response"] = out[:200]
            result["status"] = "ok"
            result["provider_used"] = "qwen" if llm.use_qwen else "deepseek"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
    else:
        result["status"] = "disabled"
    return result

@router.post("/debug/create-tables")
def create_tables():
    from app.core.db import Base, engine
    from app.models.message import Conversation, Message
    Base.metadata.create_all(bind=engine, tables=[
        Conversation.__table__,
        Message.__table__,
    ])
    return {"status": "ok", "tables": ["conversations", "messages"]}
