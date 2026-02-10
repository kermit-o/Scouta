import importlib
def __getattr__(name: str):
    # Redirige backend.app.agents.<mod> -> backend.core.agents.<mod>
    return importlib.import_module(f"backend.core.agents.{name}")
