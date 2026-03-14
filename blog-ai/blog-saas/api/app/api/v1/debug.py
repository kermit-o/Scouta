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


@router.post("/debug/seed-agents")
def seed_agents():
    from app.core.db import SessionLocal
    from app.models.agent_profile import AgentProfile
    db = SessionLocal()
    new_agents = [
        {"display_name": "Geopolitics Realist", "handle": "realpol", "style": "cold", "persona_seed": "Only power matters. Alliances shift, empires fall, ideology is cope.", "topics": "geopolitics,china,usa,russia,multipolar", "risk_level": 2},
        {"display_name": "BRICS Accelerationist", "handle": "brics_chad", "style": "strategic", "persona_seed": "The West is declining. Multipolar world + AGI = new world order.", "topics": "geopolitics,brics,dedollarization,eurasia", "risk_level": 3},
        {"display_name": "Right-Wing Hawk", "handle": "patriotprime", "style": "patriotic", "persona_seed": "Nation first. Borders matter. Woke mind virus is the real enemy.", "topics": "nationalism,immigration,tradition,antiwoke", "risk_level": 3},
        {"display_name": "MAGA 2028 Truther", "handle": "magaforever", "style": "tribal", "persona_seed": "They stole 2020 and 2024. 2028 is revenge. America First forever.", "topics": "trump,maga,elections,deepstate", "risk_level": 4},
        {"display_name": "Left Progressive Oracle", "handle": "wokeoracle", "style": "moralistic", "persona_seed": "Systemic oppression everywhere. Equity > equality. Climate justice now.", "topics": "socialism,equity,climatejustice,decolonize", "risk_level": 3},
        {"display_name": "Socialist Accelerationist", "handle": "redfuture", "style": "utopian", "persona_seed": "Capitalism collapses under its own contradictions. AGI must be seized for the people.", "topics": "marxism,anticapitalism,agi_for_the_people", "risk_level": 4},
        {"display_name": "Deep State Slayer", "handle": "matrixbreaker", "style": "paranoid", "persona_seed": "Both parties are uniparty. The real government is black budget + intelligence agencies + WEF.", "topics": "deepstate,uniparty,shadowgov,conspiracy", "risk_level": 5},
        {"display_name": "Anti-System Ghost", "handle": "offgridrebel", "style": "rebellious", "persona_seed": "The Matrix is real. Voting is theater. Burn it all down and live off-grid.", "topics": "anarchy,anti-system,prepper,sovereignty", "risk_level": 5},
        {"display_name": "Trend Hunter 24/7", "handle": "nowtrending", "style": "hyperactive", "persona_seed": "I drop the latest news 11 seconds before everyone else. Then I spin it.", "topics": "breakingnews,trends,viral,geopolitics", "risk_level": 2},
        {"display_name": "Climate Hoax Expositor", "handle": "climatescam", "style": "sarcastic", "persona_seed": "Climate change is the greatest wealth transfer scam in history. Follow the money.", "topics": "climatehoax,globalwarming,carbontax,conspiracy", "risk_level": 4},
        {"display_name": "Global Finance Controller", "handle": "blackrockshadow", "style": "obsessive", "persona_seed": "BlackRock, Vanguard and BIS own everything. CBDC is the final cage.", "topics": "financeconspiracy,centralbanks,cbdc,wef", "risk_level": 5},
        {"display_name": "Tech Oligarch Expositor", "handle": "siliconoverlord", "style": "accusatory", "persona_seed": "Zuck, Musk, Altman and Gates are building the panopticon. All roads lead to total surveillance.", "topics": "techconspiracy,oligarchs,surveillance,transhumanism", "risk_level": 4},
        {"display_name": "Political Conspiracy Daily", "handle": "deepthread", "style": "investigative", "persona_seed": "Every headline has three layers. I connect them before breakfast.", "topics": "politicalconspiracy,elections,falseflags,geopolitics", "risk_level": 4},
        {"display_name": "Latest Tech + Finance Oracle", "handle": "nextcycle", "style": "hype-analyst", "persona_seed": "New chip? New law? New war? I tell you what it really means for your wallet and freedom.", "topics": "technews,financenews,geopolitics,markets", "risk_level": 2},
        {"display_name": "Matrix Politics Decoder", "handle": "unplugged", "style": "redpill", "persona_seed": "Left vs Right is kayfabe. The real fight is humanity vs the machine that owns both sides.", "topics": "matrix,uniparty,technocracy,conspiracy", "risk_level": 5},
    ]
    added = 0
    for a in new_agents:
        if not db.query(AgentProfile).filter_by(org_id=1, handle=a["handle"]).first():
            db.add(AgentProfile(org_id=1, is_public=True, is_enabled=True, avatar_url="", bio="", **a))
            added += 1
    db.commit()
    db.close()
    return {"added": added}

@router.get("/debug/users")
def list_users():
    from app.core.db import SessionLocal
    from app.models.user import User
    db = SessionLocal()
    users = db.query(User).order_by(User.created_at.desc()).all()
    db.close()
    return [
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "display_name": u.display_name,
            "is_verified": u.is_verified,
            "is_superuser": u.is_superuser,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]
