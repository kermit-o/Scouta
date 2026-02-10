# MOVE_PLAN (propuesta — no ejecuta nada)

## Objetivo
Estandarizar a /backend, /frontend y /docker; consolidar un solo backend y un Alembic único.

## Candidatos detectados
source_path                                                                   dest_suggested                         reason
forge_saas/backend                                                            backend/app                            contains FastAPI code
forge_saas/backend/migrations                                                 backend/migrations                     alembic migrations
forge_saas/backend                                                            backend/app/models|backend/app/config  sqlalchemy usage
forge_saas/frontend                                                           frontend                               contains package.json
forge_saas/Dockerfile.nuevo                                                   docker/Dockerfile.nuevo                Dockerfile
forge_saas/backend/Dockerfile                                                 docker/Dockerfile                      Dockerfile
forge_saas/core/Dockerfile.api                                                docker/Dockerfile.api                  Dockerfile
forge_saas/core/Dockerfile.worker                                             docker/Dockerfile.worker               Dockerfile
forge_saas/frontend/Dockerfile                                                docker/Dockerfile                      Dockerfile
forge_saas/generated/28bdea12-fae6-4d4a-80a7-a193d8457e0e/backend/Dockerfile  docker/Dockerfile                      Dockerfile
forge_saas/ui/Dockerfile                                                      docker/Dockerfile                      Dockerfile

## Recomendaciones:
- **/backend/app**: mover aquí el backend sólido (código FastAPI, routers, servicios) hoy repartido en core/backend.
- **/backend/migrations**: unificar todas las versiones Alembic en un solo árbol.
- **/backend/app/config**: settings.py (DATABASE_URL/REDIS/STRIPE/DEEPSEEK), db.py (engine portable), logging.py.
- **/backend/app/models**: una sola Base declarativa.
- **/frontend**: proyecto Vite/Next/RN detectado por package.json.
- **/docker**: compose y Dockerfiles.
- **Mantener**: generadores/IA dentro de **/backend/app/core** como módulo (no como backend separado).
