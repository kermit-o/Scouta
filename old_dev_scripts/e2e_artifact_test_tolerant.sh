#!/usr/bin/env bash
set -euo pipefail

API="${API:-http://localhost:8000}"

green(){ printf "\033[32m✔ %s\033[0m\n" "$*"; }
yellow(){ printf "\033[33m● %s\033[0m\n" "$*"; }
red(){ printf "\033[31m✖ %s\033[0m\n" "$*"; }
step(){ echo; echo "== $* =="; }

step "Health"
curl -fsS "$API/api/health" | jq . >/dev/null && green "backend health OK"

step "OpenAPI: rutas clave"
if curl -fsS "$API/openapi.json" \
  | jq -r '(.paths|keys[])' \
  | grep -E '^/api/projects/.*/(requirements|plan|build|artifact)$' >/dev/null 2>&1; then
  green "rutas detectadas"
else
  yellow "no se detectaron rutas nuevas (puede ser timing o router no cargado)"
fi

step "Crear proyecto"
ID="$(curl -fsS -X POST "$API/api/projects/" -H 'content-type: application/json' -d '{"name":"demo-bash"}' | jq -r .id)"
echo "ID=$ID"

step "Requirements"
REQ='{"requirements":{"features":["crud","auth_basic"],"entities":[{"name":"Item","fields":[{"name":"id","type":"uuid"},{"name":"title","type":"string"}]}]}}'
curl -fsS -X POST "$API/api/projects/$ID/requirements" -H 'content-type: application/json' -d "$REQ" | jq -e '.ok == true' >/dev/null && green "requirements OK"

step "Plan"
curl -fsS -X POST "$API/api/projects/$ID/plan" | jq -e '.ok == true' >/dev/null && green "plan OK"

step "Build"
curl -fsS -X POST "$API/api/projects/$ID/build" | jq -e '.ok == true' >/dev/null && green "build OK"

step "Artifact HEAD"
status_head="$(curl -sS -o /dev/null -w '%{http_code}' -I "$API/api/projects/$ID/artifact" || true)"
echo "HEAD status: $status_head"
if [ "$status_head" = "200" ]; then
  headers="$(curl -sSI "$API/api/projects/$ID/artifact")"
  echo "$headers" | grep -qi '^Content-Type:.*application/zip' || yellow "Content-Type no presente (no crítico)"
  echo "$headers" | grep -qi '^ETag:'                         || yellow "ETag no presente (opcional)"
  echo "$headers" | grep -qi '^Last-Modified:'               || yellow "Last-Modified no presente (opcional)"
  echo "$headers" | grep -qi '^Content-Length:'              || yellow "Content-Length no presente (no crítico)"
  green "HEAD OK"
else
  yellow "HEAD devolvió $status_head (si es 405, la ruta no acepta HEAD pero GET probablemente funciona)"
fi

step "Artifact GET"
outfile="artifact_${ID}.zip"
curl -fsS "$API/api/projects/$ID/artifact" -o "$outfile"
if [ -s "$outfile" ]; then
  size_bytes="$(stat -c%s "$outfile" 2>/dev/null || wc -c < "$outfile")"
  echo "ZIP: $outfile ($size_bytes bytes)"
  green "GET OK"
else
  red "ZIP vacío"
  exit 1
fi

step "Verificar artifact_path persistido"
artifact_path="$(curl -fsS "$API/api/projects/$ID" | jq -r '.artifact_path // empty')"
if [ -n "$artifact_path" ]; then
  echo "artifact_path: $artifact_path"
  green "artifact_path presente"
else
  yellow "artifact_path vacío (aún se puede usar result.artifact_path)"
fi

green "E2E tolerante COMPLETADO"
