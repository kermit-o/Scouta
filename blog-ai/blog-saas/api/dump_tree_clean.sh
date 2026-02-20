#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./dump_tree_clean.sh [ROOT_DIR] [OUT_FILE]
# Examples:
#   ./dump_tree_clean.sh . /tmp/tree.txt
#   ./dump_tree_clean.sh /workspaces/Scouta/blog-ai/blog-saas/api

ROOT="${1:-.}"
OUT="${2:-/tmp/tree_clean.txt}"

cd "$ROOT"

# Common junk/system/vendor dirs to exclude (extend freely)
IGNORE_DIRS=(
  ".git"
  ".github"
  ".venv"
  "venv"
  "__pycache__"
  ".pytest_cache"
  ".mypy_cache"
  ".ruff_cache"
  ".cache"
  ".idea"
  ".vscode"
  ".DS_Store"
  "node_modules"
  "dist"
  "build"
  ".next"
  ".nuxt"
  ".tox"
  ".eggs"
  "*.egg-info"
  "site-packages"
  "pip-wheel-metadata"
  "coverage"
  ".coverage"
  "htmlcov"
  "logs"
  "log"
  "tmp"
  ".tmp"
  ".env"
  ".env.*"
  ".secrets"
  ".secrets.*"
)

# File patterns to exclude
IGNORE_FILES=(
  "*.sh"
  "*.pyc"
  "*.pyo"
  "*.pyd"
  "*.so"
  "*.dll"
  "*.dylib"
  "*.log"
  "*.sqlite"
  "*.db"
  "*.pem"
  "*.key"
  "*.p12"
  "*.pfx"
)

# Build the -I pattern for tree: single '|' separated regex-like glob pattern.
# tree -I matches against file/dir names.
PATTERN="$(printf "%s|" "${IGNORE_DIRS[@]}" "${IGNORE_FILES[@]}")"
PATTERN="${PATTERN%|}"

echo "== dump_tree_clean ==" | tee "$OUT"
echo "ROOT: $(pwd)" | tee -a "$OUT"
echo "OUT : $OUT" | tee -a "$OUT"
echo "" | tee -a "$OUT"

if command -v tree >/dev/null 2>&1; then
  # -a: include dotfiles (we'll exclude with -I)
  # -F: append indicators (/ for dir)
  # --dirsfirst: readability
  # -L: depth (raise if needed)
  # -I: ignore pattern
  tree -a -F --dirsfirst -L 6 -I "$PATTERN" | tee -a "$OUT"
else
  echo "[warn] 'tree' not found. Using fallback 'find' (less pretty)." | tee -a "$OUT"
  echo "" | tee -a "$OUT"

  # Fallback: list dirs/files excluding junk.
  # Note: this is a “good enough” tree-like outline.
  find . \
    \( \
      -path "./.git" -o -path "./.git/*" -o \
      -path "./.venv" -o -path "./.venv/*" -o \
      -path "./venv" -o -path "./venv/*" -o \
      -path "./node_modules" -o -path "./node_modules/*" -o \
      -path "./dist" -o -path "./dist/*" -o \
      -path "./build" -o -path "./build/*" -o \
      -path "./.next" -o -path "./.next/*" -o \
      -path "./.pytest_cache" -o -path "./.pytest_cache/*" -o \
      -path "./__pycache__" -o -path "./__pycache__/*" -o \
      -path "./.mypy_cache" -o -path "./.mypy_cache/*" -o \
      -path "./.ruff_cache" -o -path "./.ruff_cache/*" -o \
      -path "./.cache" -o -path "./.cache/*" -o \
      -path "./.idea" -o -path "./.idea/*" -o \
      -path "./.vscode" -o -path "./.vscode/*" \
    \) -prune -o \
    -type f \
    ! -name "*.sh" \
    ! -name "*.pyc" \
    ! -name "*.pyo" \
    ! -name "*.pyd" \
    ! -name "*.so" \
    ! -name "*.dll" \
    ! -name "*.dylib" \
    ! -name "*.log" \
    -print \
  | sed 's|^\./||' | sort | tee -a "$OUT"
fi

echo "" | tee -a "$OUT"
echo "== done ==" | tee -a "$OUT"