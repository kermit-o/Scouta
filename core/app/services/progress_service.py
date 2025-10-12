from __future__ import annotations
from typing import Dict
import threading

class ProgressTracker:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: Dict[str, Dict] = {}

    def start(self, project_id: str, message: str = "starting") -> None:
        with self._lock:
            self._store[project_id] = {"progress": 0, "status": "running", "message": message}

    def update(self, project_id: str, progress: int, message: str | None = None) -> None:
        with self._lock:
            s = self._store.setdefault(project_id, {"progress": 0, "status": "running", "message": ""})
            s["progress"] = max(0, min(progress, 100))
            if message is not None:
                s["message"] = message

    def complete(self, project_id: str, message: str = "done") -> None:
        with self._lock:
            s = self._store.setdefault(project_id, {})
            s.update({"progress": 100, "status": "done", "message": message})

    def get(self, project_id: str) -> Dict:
        with self._lock:
            return self._store.get(project_id, {"progress": 0, "status": "pending", "message": ""})

_tracker = ProgressTracker()

def get_tracker() -> ProgressTracker:
    return _tracker
