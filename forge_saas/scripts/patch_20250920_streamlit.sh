#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "🔧 Reemplazando st.experimental_rerun → st.rerun"

# Lista de archivos *.py que contienen el patrón (delimitada por NUL)
mapfile -d '' -t files < <(git grep -zl 'st\.experimental_rerun' -- '*.py' || true)

if (( ${#files[@]} == 0 )); then
  echo "ℹ️ No se encontraron ocurrencias."
  exit 0
fi

count=0
for f in "${files[@]}"; do
  if [[ -n "$f" && -f "$f" ]]; then
    sed -i -E 's/\bst\.experimental_rerun\b/st.rerun/g' "$f"
    echo "  • $f"
    ((count++)) || true
  fi
done

echo "✅ Hecho. Archivos actualizados: $count"
