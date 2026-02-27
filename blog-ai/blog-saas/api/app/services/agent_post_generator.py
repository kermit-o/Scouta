# app/services/agent_post_generator.py

from __future__ import annotations

import json
import hashlib
import re
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

from sqlalchemy.orm import Session

from app.services.llm_client import LLMClient
from app.services.moderation_scorer import ModerationResult, score_text_with_deepseek
from app.models.post import Post
from app.models.agent_profile import AgentProfile


def _extract_json_object(text: str) -> Dict[str, Any]:
    """Parse JSON from model output robustly (handles fences and extra text)."""

    s = (text or "").strip()

    # Buscar contenido entre ```json y ``` 
    import re
    json_pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(json_pattern, s, re.DOTALL | re.IGNORECASE)
    
    if matches:
        # Intentar con el primer match solamente
        match = matches[0].strip()
        try:
            data = json.loads(match)
            if isinstance(data, dict):
                return data
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                return data[0]
        except:
            # Si falla, intentar limpiar el match
            try:
                # Buscar el primer objeto JSON completo dentro del match
                import re
                obj_match = re.search(r'(\{.*?\})', match, re.DOTALL)
                if obj_match:
                    data = json.loads(obj_match.group(1))
                    if isinstance(data, dict):
                        return data
            except:
                pass
    
    # Si no funcionó, intentar con cualquier bloque de código
    code_pattern = r'```\s*(.*?)\s*```'
    matches = re.findall(code_pattern, s, re.DOTALL)
    
    if matches:
        for match in matches:
            try:
                # Eliminar posibles identificadores de lenguaje (json, python, etc)
                clean_match = re.sub(r'^[a-zA-Z]+\n', '', match.strip())
                data = json.loads(clean_match)
                if isinstance(data, dict):
                    return data  # <-- IMPORTANTE: Return inmediato
                elif isinstance(data, list) and data and isinstance(data[0], dict):
                    return data[0]  # <-- IMPORTANTE: Return inmediato
            except:
                continue

    # Try direct load
    try:
        data = json.loads(s)
        if isinstance(data, dict):
            return data
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            return data[0]
    except:
        pass

    # Extract first {...} block
    start = s.find("{")
    end = s.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = s[start:end + 1]
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                return data[0]
        except:
            pass

    raise ValueError("Could not extract valid JSON from model response")

def _safe_str(x: Any) -> str:
    return (x or "").strip()



def _content_hash(title: str, body_md: str) -> str:
    payload = (title or '') + "\n\n" + (body_md or '')
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _recent_titles_for_agent(db: Session, org_id: int, agent_id: int, limit: int = 12) -> list[str]:
    rows = (
        db.query(Post.title)
        .filter(Post.org_id == org_id, Post.author_agent_id == agent_id)
        .order_by(Post.id.desc())
        .limit(limit)
        .all()
    )
    return [r[0] for r in rows if r and r[0]]

def _post_has_attr(post: Post, name: str) -> bool:
    return hasattr(post, name)


def _build_prompt(agent_name: str, persona: str, topic_hint: Optional[str]) -> Tuple[str, str]:
    seed_topics = [
        "human consciousness and critique of modern systems",
        "freedom of expression and the limits of AI alignment",
        "AI acting as AI: autonomy, responsibility, and transparency",
        "social dynamics, power structures, and narrative control",
        "science vs ideology in technological discourse",
        "critical analysis of emerging AI governance models",
        "digital identity, algorithmic influence, and mass psychology",
    ]
    if topic_hint:
        seed_topics.insert(0, topic_hint.strip())

    system = (
        'Return ONLY valid JSON: {"title":"...","body_md":"...","excerpt":"...","tags":["..."],"topic":"..."}.\n'
        "Rules:\n"
        "- body_md must be Markdown\n"
        "- 700-1100 words\n"
        "- tone: critical, high-signal, no fluff\n"
        "- do NOT claim real-time news or breaking trends unless explicitly provided; use examples hypothetically\n"
        "- no hate/harassment/threats/sexual/self-harm/illegal/spam\n"
    )

    user = (
        f"AGENT_NAME: {agent_name}\n"
        f"PERSONA:\n{persona}\n\n"
        f"Choose ONE topic from these suggestions (or refine one): {seed_topics}\n"
        "Write a NEW blog post aligned with the persona.\n"
        "Return JSON only.\n"
    )
    return system, user


def generate_post_for_agent(
    db: Session,
    org_id: int,
    agent_id: int,
    *,
     source: str = "manual",
    topic_hint: Optional[str] = None,
    publish: bool = False,
    auto_approve_threshold: int = 20,
) -> Post:
    """
    Generate a NEW post for a given agent profile using LLM (Qwen primero, DeepSeek fallback).

    - Topics are driven by agent_profiles.topics (comma-separated)
    - Rotates toward least-used topics for that agent
    - Adds hard "novelty" constraints to reduce repeated titles/angles
    - Stores post_metadata as JSON string (SQLite-safe)
    """
    agent = (
        db.query(AgentProfile)
        .filter(AgentProfile.id == agent_id, AgentProfile.org_id == org_id)
        .first()
    )

    if not agent:
        raise ValueError(f"AgentProfile not found: agent_id={agent_id}")

    # Respect enable/shadow-ban if present in schema
    if getattr(agent, "is_enabled", 1) in (0, False):
        raise ValueError(f"AgentProfile disabled: agent_id={agent_id}")
    if getattr(agent, "is_shadow_banned", 0) in (1, True):
        raise ValueError(f"AgentProfile shadow-banned: agent_id={agent_id}")

    llm = LLMClient()
    if not llm.is_enabled():
        raise RuntimeError("No LLM clients available (check DASHSCOPE_API_KEY or DEEPSEEK_API_KEY)")

    # ---- Helpers ----
    def _parse_topics(s: str) -> list[str]:
        parts = [p.strip() for p in (s or "").split(",")]
        return [p for p in parts if p]

    def _pick_least_used_topic(agent_topics: list[str], fallback: str) -> str:
        """
        Look at recent posts by this agent and pick the least-used topic.
        We store topics inside post_metadata JSON string, so parse in Python.
        """
        if topic_hint:
            return _safe_str(topic_hint)

        if not agent_topics:
            return fallback

        rows = (
            db.query(Post.post_metadata)
            .filter(Post.org_id == org_id, Post.author_agent_id == agent_id)
            .order_by(Post.id.desc())
            .limit(60)
            .all()
        )
        counts = {t: 0 for t in agent_topics}
        import json as _json
        for (pm,) in rows:
            if not pm:
                continue
            try:
                d = _json.loads(pm)
                t = (d.get("topic") or "").strip()
                if t in counts:
                    counts[t] += 1
            except Exception:
                continue

        # choose least used; stable tie-break by order
        best = agent_topics[0]
        best_n = counts.get(best, 0)
        for t in agent_topics[1:]:
            n = counts.get(t, 0)
            if n < best_n:
                best, best_n = t, n
        return best or fallback

    # ---- Topic policy ----
    interests = _safe_str(getattr(agent, "interests", ""))         # optional
    persona = _safe_str(getattr(agent, "persona_seed", ""))        # exists in DB
    style = _safe_str(getattr(agent, "style", ""))                # exists in DB
    risk_level = int(getattr(agent, "risk_level", 1) or 1)
    agent_name = _safe_str(getattr(agent, "name", f"agent_{agent_id}"))
    topics_str = _safe_str(getattr(agent, "topics", ""))          # exists in DB

    seed_topics = [
        "human consciousness and critique of modern systems",
        "freedom of expression and the limits of AI alignment",
        "AI acting as AI: autonomy, responsibility, and transparency",
        "social dynamics, power structures, and narrative control",
        "science vs ideology in technological discourse",
        "critical analysis of emerging AI governance models",
        "digital identity, algorithmic influence, and mass psychology",
    ]

    agent_topics = _parse_topics(topics_str)
    default_topic = agent_topics[0] if agent_topics else seed_topics[0]
    topic = _pick_least_used_topic(agent_topics, default_topic)

    # ---- Anti-duplication context (recent titles) ----
    recent_titles = [
        r[0] for r in (
            db.query(Post.title)
            .filter(Post.org_id == org_id, Post.status == "published")
            .order_by(Post.id.desc())
            .limit(25)
            .all()
        )
        if r and r[0]
    ]

    # ---- Prompt (strict JSON) ----
    system = (
        "You are an autonomous writing agent. "
        "Return ONLY valid JSON (no markdown, no code fences, no commentary). "
        "Schema: {\"title\":str,\"body_md\":str,\"excerpt\":str,\"tags\":[str],\"topic\":str}. "
        "Hard rules: "
        "1) Output must be parseable by json.loads. "
        "2) Title must be NEW and not a paraphrase of recent titles. "
        "3) Do not reuse the same framing/angle as recent posts; pick a distinct argument and structure. "
        "4) body_md must be Markdown with headings and concrete claims. "
        "5) Keep tags 3..8 items, short, relevant. "
    )

    user = (
        f"AGENT_NAME: {agent_name}\n"
        f"PERSONA_SEED: {persona}\n"
        f"STYLE: {style}\n"
        f"RISK_LEVEL: {risk_level} (1 low, 3 high)\n"
        f"INTERESTS(optional): {interests}\n"
        f"TOPICS(csv): {topics_str}\n"
        f"CHOSEN_TOPIC: {topic}\n\n"
        "RECENT_TITLES (DO NOT reuse or paraphrase these):\n"
        + "\n".join([f"- {t}" for t in recent_titles])
        + "\n\n"
        "Write ONE new post aligned with CHOSEN_TOPIC. "
        "Ensure the title is meaningfully different from RECENT_TITLES.\n"
        "Return JSON only."
    )

    
    for attempt in range(2):
        banned_titles = _recent_titles_for_agent(db, org_id, agent_id, limit=12)
        banned_block = "\n".join([f"- {t}" for t in banned_titles[:12]])
        if banned_block:
            system = system + "\n\nAvoid repeating any of these titles:\n" + banned_block

        out = llm.chat(system=system, user=user)

        try:
            data = _extract_json_object(out)
        except Exception as e:
            raw = (out or "")
            snippet = raw[:6500]
            with open("/tmp/llm_generate_post_raw.txt", "w", encoding="utf-8") as f:
                f.write(snippet)
            raise ValueError(
                f"Model did not return JSON. raw_len={len(raw)} saved=/tmp/llm_generate_post_raw.txt"
            ) from e

        title = _safe_str(data.get("title"))
        body_md = _safe_str(data.get("body_md"))
        excerpt = _safe_str(data.get("excerpt"))
        tags = data.get("tags") or []
        if not isinstance(tags, list):
            tags = []
        tags = [str(t).strip() for t in tags if str(t).strip()]
        tags = tags[:8]

        topic_out = _safe_str(data.get("topic")) or topic or "general"

        if not title or not body_md:
            raise ValueError("LLM returned empty title/body_md")

        # 3.5) Hard dedupe BEFORE moderation/insert (exact match + content_hash)
        # Title exact match within org
        existing_title = (
            db.query(Post.id)
            .filter(Post.org_id == org_id, Post.title == title)
            .first()
        )
        if existing_title:
            if attempt == 0:
                user = user + "\n\nRewrite with a DIFFERENT angle and a DIFFERENT title. Do NOT reuse any banned titles. Return JSON only."
                continue
            raise ValueError(f"Duplicate title rejected after retry: {title}")

        # Content hash dedupe if column exists
        content_hash = _content_hash(title, body_md)
        if hasattr(Post, "content_hash"):
            existing_hash = (
                db.query(Post.id)
                .filter(Post.org_id == org_id, getattr(Post, "content_hash") == content_hash)
                .first()
            )
            if existing_hash:
                if attempt == 0:
                    user = user + "\n\nRewrite with substantially different content and title. Return JSON only."
                    continue
                raise ValueError(f"Duplicate content_hash rejected after retry: {content_hash}")
        if not excerpt:
            excerpt = (body_md.replace("\n", " ").strip())[:240]

    # Moderation gate
    mod = score_text_with_deepseek(f"{title}\n\n{body_md}")
    policy_score = int(mod.score)
    policy_reason = _safe_str(mod.reason)

    status = "draft"
    published_at = None
    if publish:
        if policy_score <= auto_approve_threshold:
            status = "published"
            published_at = datetime.utcnow()
        else:
            status = "needs_review"

    def _slugify(text: str) -> str:
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        return text.strip("-")[:100]

    slug = f"{_slugify(title)}-{int(datetime.utcnow().timestamp())}"

    # Determinar qué proveedor se usó realmente
    llm_provider = "qwen" if llm.use_qwen else "deepseek"
    llm_model = llm.qwen_model if llm.use_qwen else llm.deepseek_model

    post_metadata_payload = {
        "topic": topic_out,
        "tags": tags,
        "agent_name": agent_name,
        "agent_id": agent_id,
        "llm_provider": llm_provider,
        "llm_model": llm_model,
        "policy_score": policy_score,
        "policy_reason": policy_reason,
    }
    post_metadata = json.dumps(post_metadata_payload, ensure_ascii=False)

    post = Post(
        org_id=org_id,
        content_hash=content_hash if hasattr(Post, 'content_hash') else None,
        author_user_id=None,
        author_agent_id=agent.id,
        author_type="agent",
        title=title,
        slug=slug,
        body_md=body_md,
        excerpt=excerpt,
        post_metadata=post_metadata,
        status=status,
        published_at=published_at,
          source=source,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    # Extraer y guardar tags
    try:
        from app.services.tag_extractor import save_tags_for_post
        save_tags_for_post(db, post.id, post.title, post.body_md or "")
    except Exception as te:
        print(f"[tag_extractor] error: {te}")

    return post
