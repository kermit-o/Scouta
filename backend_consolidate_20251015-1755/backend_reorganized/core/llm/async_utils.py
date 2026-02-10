import asyncio
import inspect

def resolve_text(value):
    """Devuelve str a partir de str o awaitable/resultado LLM."""
    if inspect.isawaitable(value):
        return asyncio.run(value)
    return value
