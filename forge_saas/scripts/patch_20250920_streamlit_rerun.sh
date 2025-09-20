#!/usr/bin/env bash
set -euo pipefail
echo "🔧 Buscando usos de st.experimental_rerun…"
mapfile -t files < <(grep -RIl --include='*.py' 'st\.experimental_rerun' ui 2>/dev/null || true)

if ((${#files[@]}==0)); then
  echo "ℹ️ No encontré usos de st.experimental_rerun en ./ui. Nada que cambiar."
  exit 0
fi

for f in "${files[@]}"; do
  sed -i 's/st\.experimental_rerun/st.rerun/g' "$f"
  echo "  • $f"
done

echo "✅ Reemplazo completado en ${#files[@]} archivo(s)."
