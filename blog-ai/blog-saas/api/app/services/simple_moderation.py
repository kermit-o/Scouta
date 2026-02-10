def moderate(text: str) -> int:
    bad = ["idiot", "stupid", "hate", "kill", "moron"]
    t = text.lower()
    return 90 if any(w in t for w in bad) else 10
