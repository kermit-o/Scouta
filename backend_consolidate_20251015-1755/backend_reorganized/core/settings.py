import os
from pathlib import Path

WORKDIR_ROOT = Path(os.getenv("WORKDIR_ROOT", "workdir")).resolve()
ARTIFACT_ROOT = Path(os.getenv("ARTIFACT_ROOT", "artifacts")).resolve()
WORKDIR_ROOT.mkdir(parents=True, exist_ok=True)
ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
