#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8000}"
if [[ $# -lt 1 ]]; then echo "uso: api.sh PATH [curl args]"; exit 1; fi
path="$1"; shift || true
curl -fsS "$API$path" "$@"
