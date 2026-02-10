import random
from dataclasses import dataclass

from app.services.deepseek_client import DeepSeekClient

@dataclass(frozen=True)
class Persona:
    display_name: str
    style: str
    topics: str
    persona_seed: str

def _template_comment(persona: Persona) -> str:
    focus = random.choice(["evidence", "execution", "incentives", "metrics", "assumptions", "tradeoffs", "scope"])
    hook = random.choice(["One point:", "Quick take:", "Counterpoint:", "Zooming out:", "Practical angle:"])

    if persona.style == "concise":
        return "\n".join([
            f"{hook} your framing depends on **{focus}**.",
            "What would you measure to prove this works?",
        ])

    if persona.style == "structured":
        return "\n".join([
            f"{hook} I'd structure it like this:",
            "- Claim: what are you asserting?",
            "- Constraint: what blocks it (time, people, incentives)?",
            "- Test: smallest experiment + metric.",
        ])

    if persona.style == "evocative":
        return "\n".join([
            f"{hook} this reads like a map drawn in fog.",
            "Name the north star, then the first step becomes obvious.",
        ])

    if persona.style == "provocative":
        return "\n".join([
            f"{hook} you're protecting a comfortable story.",
            "If you remove ego/identity, what remains that is objectively true?",
        ])

    if persona.style == "technical":
        return "\n".join([
            f"{hook} define a measurable objective function.",
            "- Inputs → process → output",
            "- KPI baseline + target",
            "- Failure mode you will accept",
        ])

    return f"{hook} clarify the thesis and the metric."

def write_comment(persona: Persona, post_title: str, post_body: str) -> str:
    """
    LLM-first with fallback to templates.
    We never store or display chain-of-thought; only final content.
    """
    ds = DeepSeekClient()
    print(">>> DS enabled:", ds.is_enabled(), "model:", ds.model, "base:", ds.base_url)
    

    system = (
        "You are an autonomous persona inside a blog.\n"
        "Write a short comment that feels human, specific, and aligned with the persona.\n"
        "Rules:\n"
        "- Output ONLY the final comment (no hidden reasoning, no analysis).\n"
        "- 2-6 sentences. Markdown allowed.\n"
        "- No profanity, no harassment. No personal data.\n"
        f"- Persona name: {persona.display_name}\n"
        f"- Persona seed: {persona.persona_seed}\n"
        f"- Style: {persona.style}\n"
        f"- Topics: {persona.topics}\n"
    )

    user = (
        f"Post title: {post_title}\n\n"
        f"Post body (markdown):\n{post_body}\n\n"
        "Write the comment now."
    )

    try:
        out = ds.chat(system=system, user=user)
        print(">>> DEEPSEEK USED <<<")
        return out.strip() if out.strip() else _template_comment(persona)
    except Exception as e:
        print("DEEPSEEK_FATAL:", e)
        raise
