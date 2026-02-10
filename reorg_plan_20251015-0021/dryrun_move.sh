#!/usr/bin/env bash
# Este script SOLO imprime los movimientos sugeridos. No mueve nada.
set +e
MAP="move_map.tsv"
[ -f "$MAP" ] || { echo "No existe $MAP (ejecuta el escáner primero)"; exit 0; }
echo "### DRY-RUN (echo de movimientos sugeridos) ###"
while IFS=$'\t' read -r SRC DST REASON; do
  [ "$SRC" = "source_path" ] && continue
  [ -e "$SRC" ] || { echo "# (faltante) $SRC — $REASON"; continue; }
  echo "mkdir -p $(dirname "$DST")"
  echo "git mv \"$SRC\" \"$DST\"   # $REASON"
done < "$MAP"
