#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== diet_ai diagnostic ==="
echo
echo "[*] Python version:"
python3 --version 2>/dev/null || python --version 2>/dev/null || echo "  (python not found)"
echo
echo "[*] Docker version:"
docker --version 2>/dev/null || echo "  (docker not found)"
echo

diag_project() {
  local name="$1"
  local rel_path="$2"
  local path="$ROOT_DIR/$rel_path"

  echo
  echo "========================================"
  echo "Project: $name"
  echo "Path:    $rel_path"
  echo "========================================"

  if [[ ! -d "$path" ]]; then
    echo "  -> Directory not found, skipping."
    return
  fi

  # Basic key files
  for f in Dockerfile docker-compose.yml requirements.txt requirements_final.txt requirements.optimized.txt; do
    if [[ -f "$path/$f" ]]; then
      echo "  - Found: $f"
    fi
  done

  # Look for main.py entrypoints (up to depth 4 to avoid huge noise)
  echo "  - Searching for main.py entrypoints..."
  mapfile -t mains < <(find "$path" -maxdepth 4 -type f -name "main.py" 2>/dev/null | sort || true)
  if ((${#mains[@]} == 0)); then
    echo "    (no main.py found up to depth 4)"
  else
    for m in "${mains[@]}"; do
      echo "    * $m"
      if grep -q "FastAPI" "$m" 2>/dev/null; then
        echo "      framework: FastAPI (detected in file)"
      fi
      if grep -q "Flask" "$m" 2>/dev/null; then
        echo "      framework: Flask (detected in file)"
      fi
    done
  fi

  # Look for health endpoints / files
  echo "  - Searching for health-related files..."
  mapfile -t health_files < <(find "$path" -maxdepth 5 -type f \( -name "health.py" -o -name "health_check_fix.py" \) 2>/dev/null | sort || true)
  if ((${#health_files[@]} == 0)); then
    echo "    (no health-related files found up to depth 5)"
  else
    for hf in "${health_files[@]}"; do
      echo "    * $hf"
    done
  fi

  # Look for core domain models: diet, inventory, recipe, user
  echo "  - Searching for core domain model files..."
  mapfile -t model_files < <(find "$path" -maxdepth 6 -type f \( -name "diet.py" -o -name "inventory.py" -o -name "recipe.py" -o -name "user.py" \) 2>/dev/null | sort || true)
  if ((${#model_files[@]} == 0)); then
    echo "    (no diet/inventory/recipe/user model files found up to depth 6)"
  else
    for mf in "${model_files[@]}"; do
      echo "    * $mf"
    done
  fi

  # Quick note about api layout
  echo "  - API layout hints..."
  if [[ -d "$path/backend/api" ]]; then
    echo "    backend/api exists"
    find "$path/backend/api" -maxdepth 3 -type f -name "*.py" 2>/dev/null | sed 's/^/      - /' || true
  elif [[ -d "$path/api" ]]; then
    echo "    api exists at root"
    find "$path/api" -maxdepth 3 -type f -name "*.py" 2>/dev/null | sed 's/^/      - /' || true
  else
    echo "    (no api folder detected at root or backend/api)"
  fi
}

diag_project "diet_ai (root version)" "diet_ai"
diag_project "diet_ai_complete" "diet_ai_complete"
diag_project "diet_ai_production" "diet_ai_production"
diag_project "diet_ai_final" "diet_ai_final"
diag_project "dieta-backend" "dieta-backend"
diag_project "dieta-funcional" "dieta-funcional"

echo
echo "=== Diagnostic finished ==="
