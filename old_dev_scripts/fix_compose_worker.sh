#!/usr/bin/env bash
set -euo pipefail
F="docker-compose.override.yml"

# Si no existe, lo creamos básico con un único worker
if [ ! -f "$F" ]; then
  cat > "$F" <<'YAML'
services:
  worker:
    image: forge_saas-backend
    depends_on:
      postgres:
        condition: service_healthy
        required: true
    environment:
      DATABASE_URL: postgresql+psycopg2://forge:forge@postgres:5432/forge
    command: >
      sh -lc 'python -m app.services.scheduler'
YAML
  echo "Creado $F"
  exit 0
fi

# 1) Hacemos backup
cp -n "$F" "$F.bak" || true

# 2) Extraemos todas las definiciones 'worker:' y nos quedamos con la ÚLTIMA
awk '
/^services:/{in_services=1}
{
  if(in_services){
    print
  }
}
' "$F" > /tmp/_svc.yml

# Normaliza: si hay más de un bloque "worker:", deja solo el último
# (vamos a reconstruir el archivo dejando un único worker al final)
awk '
BEGIN{print "services:"; in=0}
{
  if($1=="worker:"){in=1; buf=""; print ""; next}
  if(in && match($0,/^[^ ]/)){in=0} # sale cuando vuelve al margen
  if(!in && $0!="" && $0!="services:"){print $0}
}
END{
  # Append un worker único estandarizado:
  print "  worker:";
  print "    image: forge_saas-backend";
  print "    depends_on:";
  print "      postgres:";
  print "        condition: service_healthy";
  print "        required: true";
  print "    environment:";
  print "      DATABASE_URL: postgresql+psycopg2://forge:forge@postgres:5432/forge";
  print "    command: >";
  print "      sh -lc '\''python -m app.services.scheduler'\''";
}
' /tmp/_svc.yml > "$F.clean"

mv "$F.clean" "$F"

echo "OK: $F normalizado (backup en $F.bak)"
