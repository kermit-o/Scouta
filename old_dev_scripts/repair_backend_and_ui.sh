#!/usr/bin/env bash
# repair_backend_and_ui.sh
# Arregla conectividad UI ⇄ Backend y conflictos del puerto 8000.
# Genera un informe en la raíz del proyecto.

set -eu

TS="$(date +"%Y-%m-%d_%H-%M-%S")"
OUT_FILE="$(pwd)/repair_${TS}.txt"
exec > >(tee -a "$OUT_FILE") 2>&1

section(){ printf "\n\033[1;34m== %s ==\033[0m\n" "$1"; }
ok(){ printf "  \033[32m✔ %s\033[0m\n" "$1"; }
warn(){ printf "  \033[33m⚠ %s\033[0m\n" "$1"; }
err(){ printf "  \033[31m✖ %s\033[0m\n" "$1"; }

section "Inicio de reparación"
echo "Fecha: $(date -Is)"
echo "Ruta:  $(pwd)"
echo "Log:   $OUT_FILE"

# -------------------------------------------------------------------
# 1) Detectar contenedores y redes
# -------------------------------------------------------------------
section "Contenedores activos"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" || true

UI_CONT=$(docker ps --format '{{.Names}}' | grep -E '(^|-)ui(-|$)|streamlit' | head -1 || true)
BE_CONT=$(docker ps --format '{{.Names}}' | grep -E '(^|-)backend(-|$)' | head -1 || true)

echo "  UI detectada:      ${UI_CONT:-<ninguna>}"
echo "  Backend detectado: ${BE_CONT:-<ninguno>}"

# -------------------------------------------------------------------
# 2) Liberar puerto 8000 si está ocupado
# -------------------------------------------------------------------
section "Liberando puerto 8000 si está ocupado"

# Contenedores que publican 8000 en el host
OCC_CONT=$(docker ps --format '{{.Names}}\t{{.Ports}}' \
  | awk '/:8000->/ {print $1}' | xargs -r echo || true)

if [[ -n "${OCC_CONT// /}" ]]; then
  warn "Puerto 8000 ocupado por: $OCC_CONT"
  echo "Deteniendo contenedores que usan 8000…"
  for c in $OCC_CONT; do
    docker stop "$c" >/dev/null 2>&1 || true
    docker rm   "$c" >/dev/null 2>&1 || true
    echo "  - $c detenido y eliminado."
  done
else
  ok "El puerto 8000 no parece ocupado por Docker."
fi

# Procesos locales (no Docker)
if command -v lsof >/dev/null 2>&1; then
  if lsof -i :8000 -sTCP:LISTEN -nP 2>/dev/null | grep -q .; then
    warn "Hay procesos locales escuchando en 8000:"
    lsof -i :8000 -sTCP:LISTEN -nP || true
    echo "Intentando terminar procesos locales en 8000…"
    lsof -t -i :8000 -sTCP:LISTEN -nP | xargs -r kill -9 || true
  else
    ok "No hay procesos locales en 8000."
  fi
fi

# -------------------------------------------------------------------
# 3) Limpiar huérfanos que rompen DNS y nombre 'backend'
# -------------------------------------------------------------------
section "Limpiando contenedores huérfanos/antiguos"
for pat in 'backend-complete' 'backend-simple' 'forge-backend' 'forge-backend-*'; do
  docker ps -a --format '{{.Names}}' | grep -E "$pat" | while read -r c; do
    [[ -z "$c" ]] && continue
    echo "  - Eliminando $c"
    docker stop "$c" >/dev/null 2>&1 || true
    docker rm   "$c" >/dev/null 2>&1 || true
  done
done
ok "Limpieza básica realizada."

# -------------------------------------------------------------------
# 4) Levantar backend y UI con docker compose
# -------------------------------------------------------------------
section "Levantando backend y UI (docker compose)"
# No tumbamos postgres; solo backend/UI y huérfanos
docker compose up -d --build --remove-orphans backend ui

sleep 3
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(backend|ui)" || true

# Refrescar detección
UI_CONT=$(docker ps --format '{{.Names}}' | grep -E '(^|-)ui(-|$)|streamlit' | head -1 || true)
BE_CONT=$(docker ps --format '{{.Names}}' | grep -E '(^|-)backend(-|$)' | head -1 || true)

if [[ -z "${BE_CONT:-}" ]]; then
  err "No se logró levantar un contenedor llamado 'backend'."
  echo "Revisa los logs: docker compose logs backend --tail=200"
fi

# -------------------------------------------------------------------
# 5) Verificar que UI y backend comparten red
# -------------------------------------------------------------------
section "Verificando redes compartidas UI ⇄ backend"
if [[ -n "${UI_CONT:-}" && -n "${BE_CONT:-}" ]]; then
  UI_NETS=$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{printf "%s\n" $k}}{{end}}' "$UI_CONT" 2>/dev/null | sort)
  BE_NETS=$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{printf "%s\n" $k}}{{end}}' "$BE_CONT" 2>/dev/null | sort)
  echo "  Redes UI:"
  echo "$UI_NETS" | sed 's/^/    - /'
  echo "  Redes Backend:"
  echo "$BE_NETS" | sed 's/^/    - /'
  COMMON_NET=$(comm -12 <(echo "$UI_NETS") <(echo "$BE_NETS") | head -1 || true)
  if [[ -n "$COMMON_NET" ]]; then
    ok "Comparten red: $COMMON_NET"
  else
    warn "No comparten red. Conectando backend a la red de la UI…"
    # Tomamos la primera red de UI
    UI_NET=$(echo "$UI_NETS" | head -1)
    if [[ -n "$UI_NET" && -n "${BE_CONT:-}" ]]; then
      docker network connect "$UI_NET" "$BE_CONT" 2>/dev/null || true
      ok "Conectado $BE_CONT → $UI_NET"
    fi
  fi
else
  warn "No se detectaron ambos contenedores para comprobar redes."
fi

# -------------------------------------------------------------------
# 6) Verificaciones de salud (host y dentro de UI)
# -------------------------------------------------------------------
section "Health desde HOST"
HOST_HEALTH=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health || echo "000")
echo "  GET http://localhost:8000/api/health -> $HOST_HEALTH"
[[ "$HOST_HEALTH" == "200" ]] && ok "Backend responde en el host." || warn "Backend aún no responde en el host."

section "Verificación dentro del contenedor UI"
if [[ -n "${UI_CONT:-}" ]]; then
  docker exec "$UI_CONT" /bin/sh -lc 'python - <<PY
import os, socket, urllib.request
be = os.getenv("BACKEND_URL","http://backend:8000")
print("  BACKEND_URL =", be)
try:
    ip = socket.gethostbyname("backend")
    print("  DNS backend  =", ip)
except Exception as e:
    print("  DNS ERROR    =", e)
try:
    with urllib.request.urlopen(be+"/api/health", timeout=5) as r:
        print("  HTTP health  =", r.status, r.reason)
        print("  Body         =", (r.read()[:200]).decode("utf-8","ignore"))
except Exception as e:
    print("  HTTP ERROR   =", e)
PY' 2>&1 || true
else
  warn "Contenedor UI no encontrado; no se puede probar desde dentro."
fi

# -------------------------------------------------------------------
# 7) Reinicio (si el backend tardó)
# -------------------------------------------------------------------
if [[ "$HOST_HEALTH" != "200" ]]; then
  section "Reintento rápido"
  echo "Esperando 3s y reintentando health…"
  sleep 3
  HOST_HEALTH=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health || echo "000")
  echo "  GET http://localhost:8000/api/health -> $HOST_HEALTH"
  [[ "$HOST_HEALTH" == "200" ]] && ok "Backend arriba tras reintento." || warn "Sigue sin responder."
fi

# -------------------------------------------------------------------
# 8) Sugerencias finales
# -------------------------------------------------------------------
section "Sugerencias"
echo "  - Si la UI sigue mostrando 'Name or service not known':"
echo "      * Asegúrate de que exista el servicio 'backend' en docker-compose."
echo "      * Revisa logs: docker compose logs backend --tail=200"
echo "  - Si prefieres que los links visibles usen localhost:"
echo "      * Exporta y recrea: BACKEND_PUBLIC_URL=http://localhost:8000"
echo "        ej.: BACKEND_PUBLIC_URL=http://localhost:8000 docker compose up -d ui"
echo "  - Para limpiar todo lo huérfano: docker compose up -d --build --remove-orphans"

echo
ok "Reparación finalizada."
echo "Informe: $OUT_FILE"
