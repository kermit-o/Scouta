#!/usr/bin/env bash
# dev/forge_watch.sh
# Monitor for Forge SaaS AI (backend FastAPI + UI Streamlit) in GitHub Workspaces.
set -Eeuo pipefail

# ---------- Config ----------
API="${API:-http://localhost:8000}"
UI_URL="${UI_URL:-http://localhost:8501}"
DC="${DC:-docker compose}"
TAIL="${TAIL:-120}"
PROJECT_HINT="${PROJECT_HINT:-forge}"   # para filtrar docker stats/ps
# ----------------------------

green(){ printf "\033[32m✔ %s\033[0m\n" "$*"; }
yellow(){ printf "\033[33m● %s\033[0m\n" "$*"; }
red(){ printf "\033[31m✖ %s\033[0m\n" "$*"; }
title(){ echo; printf "\033[1m== %s ==\033[0m\n" "$*"; }

req(){ command -v "$1" >/dev/null 2>&1 || { red "Falta '$1' en el entorno"; exit 1; }; }

health_backend(){
  title "Backend health ($API/api/health)"
  if out="$(curl -fsS "$API/api/health" 2>/dev/null)"; then
    echo "$out" | sed 's/^/  /'
    green "Backend OK"
  else
    red "Backend no responde en $API"
  fi
}

health_ui(){
  title "UI check ($UI_URL)"
  if curl -fsS -o /dev/null "$UI_URL"; then
    green "UI accesible"
  else
    yellow "No se pudo acceder a $UI_URL (puede estar arrancando)"
  fi
}

cmd_ps(){
  title "Servicios (docker compose ps)"
  $DC ps
}

cmd_ports(){
  title "Puertos publicados"
  $DC ps --format json 2>/dev/null | jq -r '.[] | "\(.Name) -> \(.Publishers[]?.PublishedPort // "N/A")"' 2>/dev/null || {
    # fallback sin jq
    $DC ps
  }
}

cmd_logs(){
  title "Últimos logs (tail $TAIL)"
  $DC logs --tail="$TAIL" backend ui || $DC logs --tail="$TAIL"
}

cmd_logs_follow(){
  title "Logs en vivo (Ctrl+C para salir)"
  # Prefijos legibles por servicio
  { $DC logs -f --tail=0 backend | sed -u 's/^/[backend] /' & } ;
  { $DC logs -f --tail=0 ui      | sed -u 's/^/[ui     ] /' & } ;
  wait
}

cmd_logs_ui(){  title "UI logs (follow)"; $DC logs -f --tail=50 ui; }
cmd_logs_backend(){ title "Backend logs (follow)"; $DC logs -f --tail=50 backend; }

cmd_stats(){
  title "docker stats (filtrando '$PROJECT_HINT')"
  docker ps --format '{{.ID}}\t{{.Names}}' | awk -v k="$PROJECT_HINT" 'index($2,k){print $1}' | xargs -r docker stats --no-stream
}

cmd_rebuild(){
  title "Rebuild + up -d (ui & backend)"
  $DC up -d --build ui backend
  health_backend
  health_ui
}

cmd_openapi(){
  title "OpenAPI (rutas)"
  if command -v jq >/dev/null 2>&1; then
    curl -fsS "$API/openapi.json" | jq '.paths | keys' || yellow "No se pudo leer /openapi.json"
  else
    curl -fsS "$API/openapi.json" | head -n 40 || yellow "No se pudo leer /openapi.json"
  fi
}

cmd_list(){
  title "LISTING rápido"
  cmd_ps
  cmd_ports || true
  health_backend
  health_ui
  cmd_logs
}

cmd_watch(){
  # Loop ligero: estado + salud cada N segundos
  interval="${1:-5}"
  title "WATCH (cada ${interval}s). Ctrl+C para salir."
  while true; do
    clear
    echo "(API=$API | UI_URL=$UI_URL | $(date '+%F %T'))"
    cmd_ps
    echo
    health_backend
    health_ui
    echo
    echo "— Últimos $TAIL logs combinados —"
    $DC logs --tail="$TAIL" backend ui 2>/dev/null | tail -n "$TAIL"
    sleep "$interval"
  done
}

usage(){
  cat <<-EOF
Usage: $(basename "$0") <comando>
Comandos:
  list               Estado rápido (ps/puertos/health/logs)
  ps                 docker compose ps
  ports              Puertos publicados
  health             Comprueba backend y UI
  openapi            Muestra rutas de /openapi.json (si existe)
  logs               Logs recientes de ui+backend
  follow             Logs en vivo de ui+backend con prefijos
  logs:ui            Solo logs de la UI (follow)
  logs:backend       Solo logs del backend (follow)
  stats              docker stats (filtra por PROJECT_HINT="${PROJECT_HINT}")
  rebuild            Rebuild y levanta ui+backend
  watch [seg]        Refresco continuo (default 5s)

Variables útiles:
  API=$API
  UI_URL=$UI_URL
  DC="$DC"
  TAIL="$TAIL"
  PROJECT_HINT="$PROJECT_HINT"
EOF
}

main(){
  req docker
  req curl
  cmd="${1:-list}"
  shift || true
  case "$cmd" in
    list) cmd_list ;;
    ps) cmd_ps ;;
    ports) cmd_ports ;;
    health) health_backend; health_ui ;;
    openapi) cmd_openapi ;;
    logs) cmd_logs ;;
    follow) cmd_logs_follow ;;
    logs:ui) cmd_logs_ui ;;
    logs:backend) cmd_logs_backend ;;
    stats) cmd_stats ;;
    rebuild) cmd_rebuild ;;
    watch) cmd_watch "${1:-5}" ;;
    -h|--help|help) usage ;;
    *) red "Comando desconocido: $cmd"; usage; exit 1 ;;
  esac
}

main "$@"
