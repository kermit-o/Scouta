# Reorg Plan — 2025-10-15 00:21:37 UTC
- Repo: Scouta
- Branch: main
- Último commit: 9cb6384 2025-10-15 00:14:04 +0000 — chore(structure): unify core backend into backend/, standardize layout and config

## Árbol (niveles 1–3, sin .git/.venv/node_modules)
.
├── .pytest_cache
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   ├── README.md
│   └── v
│       └── cache
├── .vscode
├── README.md
├── backup_repo_a
│   ├── .env
│   ├── .pytest_cache
│   │   ├── .gitignore
│   │   ├── CACHEDIR.TAG
│   │   ├── README.md
│   │   └── v
│   ├── .vscode
│   ├── README.md
│   ├── backup_repo
│   │   ├── .env
│   │   ├── .vscode
│   │   ├── README.md
│   │   ├── backup_repo
│   │   ├── forge_saas
│   │   ├── package-lock.json
│   │   └── run.txt
│   ├── backup_repo_a
│   ├── forge_saas
│   │   ├── .env
│   │   ├── .gitignore
│   │   ├── .uvicorn.pid
│   │   ├── Dockerfile.nuevo
│   │   ├── README.md
│   │   ├── _extract
│   │   ├── agents
│   │   ├── alembic.ini
│   │   ├── backend
│   │   ├── components
│   │   ├── config
│   │   ├── core
│   │   ├── database
│   │   ├── deployment
│   │   ├── docker-compose-clean.yml
│   │   ├── docker-compose.prod.yml
│   │   ├── docker-compose.worker.yml
│   │   ├── docker-compose.yml
│   │   ├── encoded.txt
│   │   ├── files.txt
│   │   ├── find_api_calls.sh
│   │   ├── find_port.py
│   │   ├── forge_saas_backup_20250917_164711.tar.gz
│   │   ├── forge_saas_backup_20250917_164711.tar.gz.sha256
│   │   ├── frontend
│   │   ├── generated
│   │   ├── generated_projects
│   │   ├── generators
│   │   ├── launch_system.sh
│   │   ├── local_storage
│   │   ├── logs
│   │   ├── main.py
│   │   ├── main_corrected.py
│   │   ├── migrations
│   │   ├── monitoring_system.py
│   │   ├── oracle_monitor.py
│   │   ├── project_types
│   │   ├── requirements.txt
│   │   ├── setup.py
│   │   ├── shared_components
│   │   ├── start.sh
│   │   ├── start_all_services.sh
│   │   ├── start_complete_system.sh
│   │   ├── start_forge.sh
│   │   ├── start_production.sh
│   │   ├── start_simple.sh
│   │   ├── start_system.sh
│   │   ├── stop.sh
│   │   ├── stop_all_services.sh
│   │   ├── stop_system.sh
│   │   ├── structure.txt
│   │   ├── templates
│   │   ├── tests
│   │   ├── tsconfig.json
│   │   ├── ui
│   │   ├── vite.config.js
│   │   └── websocat
│   ├── package-lock.json
│   └── run.txt
├── dev.sqlite3
├── env.example
├── forge_saas
│   ├── .env
│   ├── .gitignore
│   ├── .uvicorn.pid
│   ├── Dockerfile.nuevo
│   ├── README.md
│   ├── _extract
│   ├── agents
│   │   ├── deepseek_client.py
│   │   ├── deepseek_client_direct.sh
│   │   ├── orchestrator
│   │   └── specialists
│   ├── alembic.ini
│   ├── backend
│   │   ├── Dockerfile
│   │   ├── app
│   │   ├── debug_schema.py
│   │   ├── forge_dev.db
│   │   ├── generated
│   │   ├── init_db.py
│   │   ├── migrations
│   │   └── requirements.txt
│   ├── components
│   │   └── Auth
│   ├── config
│   │   ├── __init__.py
│   │   ├── ai_config.py
│   │   ├── logging.py
│   │   └── settings.py
│   ├── core
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.worker
│   │   ├── alembic.ini
│   │   ├── app
│   │   ├── auth
│   │   ├── core
│   │   ├── database
│   │   ├── db
│   │   ├── entrypoint.sh
│   │   ├── generated
│   │   ├── generators
│   │   ├── integrations
│   │   ├── migrations
│   │   ├── models
│   │   ├── package-lock.json
│   │   ├── payments
│   │   ├── scripts
│   │   ├── services
│   │   └── utils
│   ├── database
│   │   └── migrations
│   ├── deployment
│   │   ├── deployer.py
│   │   ├── docker
│   │   ├── kubernetes
│   │   └── serverless
│   ├── docker-compose-clean.yml
│   ├── docker-compose.prod.yml
│   ├── docker-compose.worker.yml
│   ├── docker-compose.yml
│   ├── encoded.txt
│   ├── files.txt
│   ├── find_api_calls.sh
│   ├── find_port.py
│   ├── forge_saas_backup_20250917_164711.tar.gz
│   ├── forge_saas_backup_20250917_164711.tar.gz.sha256
│   ├── frontend
│   │   ├── .dockerignore
│   │   ├── .env.local
│   │   ├── .next
│   │   ├── Dockerfile
│   │   ├── app
│   │   ├── components
│   │   ├── index.html
│   │   ├── jsconfig.json
│   │   ├── lib
│   │   ├── next-env.d.ts
│   │   ├── next.config.mjs
│   │   ├── package-lock.json
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vite.config.js
│   ├── generated
│   │   ├── 28bdea12-fae6-4d4a-80a7-a193d8457e0e
│   │   └── 28bdea12-fae6-4d4a-80a7-a193d8457e0e.zip
│   ├── generated_projects
│   ├── generators
│   │   ├── __init__.py
│   │   ├── ai
│   │   ├── backend
│   │   ├── blockchain
│   │   ├── code_validator.py
│   │   ├── desktop
│   │   ├── frontend
│   │   ├── minimal_engine.py
│   │   ├── mobile
│   │   ├── simple_engine.py
│   │   ├── specialized
│   │   └── template_engine.py
│   ├── launch_system.sh
│   ├── local_storage
│   │   └── projects
│   ├── logs
│   ├── main.py
│   ├── main_corrected.py
│   ├── migrations
│   │   └── versions
│   ├── monitoring_system.py
│   ├── oracle_monitor.py
│   ├── project_types
│   │   ├── __init__.py
│   │   ├── ai
│   │   ├── ai_agent
│   │   ├── api
│   │   ├── api_service
│   │   ├── blockchain_dapp
│   │   ├── chrome_extension
│   │   ├── desktop
│   │   ├── desktop_app
│   │   ├── extension
│   │   ├── game
│   │   ├── mobile
│   │   ├── mobile_app
│   │   ├── web
│   │   └── web_app
│   ├── requirements.txt
│   ├── setup.py
│   ├── shared_components
│   │   ├── __init__.py
│   │   ├── auth
│   │   ├── database
│   │   ├── email
│   │   ├── payment
│   │   └── storage
│   ├── start.sh
│   ├── start_all_services.sh
│   ├── start_complete_system.sh
│   ├── start_forge.sh
│   ├── start_production.sh
│   ├── start_simple.sh
│   ├── start_system.sh
│   ├── stop.sh
│   ├── stop_all_services.sh
│   ├── stop_system.sh
│   ├── structure.txt
│   ├── templates
│   │   ├── base
│   │   ├── deployment
│   │   └── stacks
│   ├── tests
│   │   ├── conftest.py
│   │   ├── e2e
│   │   ├── integration
│   │   ├── test_agent.py
│   │   ├── test_artifact_route.py
│   │   ├── test_health.py
│   │   ├── test_openapi.py
│   │   ├── test_projects_crud.py
│   │   ├── test_projects_crud_extended.py
│   │   ├── test_security_headers.py
│   │   └── unit
│   ├── tsconfig.json
│   ├── ui
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   ├── requirements.txt
│   │   └── src
│   ├── vite.config.js
│   └── websocat
├── package-lock.json
├── reorg_plan_20251015-0021
│   └── INVENTORY.md
└── run.txt

121 directories, 141 files

## Archivos grandes (top 30 por tamaño — trackeados por git)
97M	backup_repo_a/backup_repo/forge_saas/frontend/node_modules/@firebase
97M	backup_repo_a/forge_saas/frontend/node_modules/@firebase
100M	backup_repo_a/.venv/lib
100M	backup_repo_a/.venv/lib/python3.12
100M	backup_repo_a/.venv/lib/python3.12/site-packages
100M	backup_repo_a/backup_repo/.venv/lib
100M	backup_repo_a/backup_repo/.venv/lib/python3.12
100M	backup_repo_a/backup_repo/.venv/lib/python3.12/site-packages
101M	backup_repo_a/.venv
101M	backup_repo_a/backup_repo/.venv
101M	backup_repo_a/backup_repo/forge_saas/frontend/node_modules/next/dist/compiled
101M	backup_repo_a/forge_saas/frontend/node_modules/next/dist/compiled
137M	backup_repo_a/backup_repo/forge_saas/frontend/node_modules/@next/swc-linux-x64-gnu
137M	backup_repo_a/backup_repo/forge_saas/frontend/node_modules/@next/swc-linux-x64-musl
137M	backup_repo_a/forge_saas/frontend/node_modules/@next/swc-linux-x64-gnu
137M	backup_repo_a/forge_saas/frontend/node_modules/@next/swc-linux-x64-musl
153M	backup_repo_a/backup_repo/forge_saas/frontend/node_modules/next/dist
153M	backup_repo_a/forge_saas/frontend/node_modules/next/dist
154M	backup_repo_a/backup_repo/forge_saas/frontend/node_modules/next
154M	backup_repo_a/forge_saas/frontend/node_modules/next
273M	backup_repo_a/backup_repo/forge_saas/frontend/node_modules/@next
273M	backup_repo_a/forge_saas/frontend/node_modules/@next
731M	backup_repo_a/backup_repo/forge_saas/frontend/node_modules
731M	backup_repo_a/forge_saas/frontend/node_modules
816M	backup_repo_a/backup_repo/forge_saas/frontend
816M	backup_repo_a/forge_saas/frontend
914M	backup_repo_a/backup_repo/forge_saas
914M	backup_repo_a/forge_saas
1.1G	backup_repo_a/backup_repo
2.1G	backup_repo_a

## Dependencias Python (requirements*/pyproject)

## Docker/Compose
- Dockerfiles:
backend/app/core/Dockerfile.api
backend/app/core/Dockerfile.worker
backend/app/core/generated/7187fc2e-b0e9-4fec-84cd-e47ab93b75f9/backend/Dockerfile
backend/app/core/generated/d6132443-6d6d-4bee-bcaa-b18ee1708747/backend/Dockerfile
backend/app/core/generated/full-demo/Dockerfile
forge_saas/Dockerfile.nuevo
forge_saas/backend/Dockerfile
forge_saas/core/Dockerfile.api
forge_saas/core/Dockerfile.worker
forge_saas/frontend/Dockerfile
forge_saas/generated/28bdea12-fae6-4d4a-80a7-a193d8457e0e/backend/Dockerfile
forge_saas/ui/Dockerfile
monorepo_v2/backend/Dockerfile
monorepo_v2/backend/core/Dockerfile.api
monorepo_v2/backend/core/Dockerfile.worker
monorepo_v2/backend/core/generated/7187fc2e-b0e9-4fec-84cd-e47ab93b75f9/backend/Dockerfile
monorepo_v2/backend/core/generated/d6132443-6d6d-4bee-bcaa-b18ee1708747/backend/Dockerfile
monorepo_v2/backend/core/generated/full-demo/Dockerfile
monorepo_v2/docker/Dockerfile.backend
monorepo_v2/docker/Dockerfile.frontend
monorepo_v2/docker/Dockerfile.streamlit
monorepo_v2/frontend/Dockerfile

- docker-compose:*
forge_saas/docker-compose.yml
forge_saas/local_storage/projects/test_project/docker-compose.yml
monorepo_v2/docker/docker-compose.yml

## Alembic/Migraciones
forge_saas/core/migrations/versions
forge_saas/migrations/versions
forge_saas/backend/migrations/versions
backup_repo_a/backup_repo/forge_saas/core/migrations/versions
backup_repo_a/backup_repo/forge_saas/migrations/versions
backup_repo_a/backup_repo/forge_saas/backend/migrations/versions
backup_repo_a/forge_saas/core/migrations/versions
backup_repo_a/forge_saas/migrations/versions
backup_repo_a/forge_saas/backend/migrations/versions
backend/app/core/migrations/versions/__init__.py
backend/migrations/versions/1bb4a971bc3c_init.py
backend/migrations/versions/1f53bda92b4b_init.py
backend/migrations/versions/20250928_0001_jobs_agent_runs_artifacts.py
backend/migrations/versions/731f548685d5_add_missing_project_columns.py
backend/migrations/versions/a3683ddb987c_init.py
backend/migrations/versions/a5d3661ccee5_add_size_and_sha256_columns_to_artifacts.py
backend/migrations/versions/ba37eabeee95_fix_artifact_model.py
backend/migrations/versions/bd142ee8c0ea_initial_migration.py
forge_saas/backend/migrations/versions/1bb4a971bc3c_init.py
forge_saas/backend/migrations/versions/1f53bda92b4b_init.py
forge_saas/backend/migrations/versions/20250928_0001_jobs_agent_runs_artifacts.py
forge_saas/backend/migrations/versions/731f548685d5_add_missing_project_columns.py
forge_saas/backend/migrations/versions/a3683ddb987c_init.py
forge_saas/backend/migrations/versions/a5d3661ccee5_add_size_and_sha256_columns_to_artifacts.py
forge_saas/backend/migrations/versions/ba37eabeee95_fix_artifact_model.py
forge_saas/backend/migrations/versions/bd142ee8c0ea_initial_migration.py
monorepo_v2/backend/core/migrations/versions/__init__.py
monorepo_v2/backend/migrations/versions/1bb4a971bc3c_init.py
monorepo_v2/backend/migrations/versions/1f53bda92b4b_init.py
monorepo_v2/backend/migrations/versions/20250928_0001_jobs_agent_runs_artifacts.py
monorepo_v2/backend/migrations/versions/731f548685d5_add_missing_project_columns.py
monorepo_v2/backend/migrations/versions/__init__.py
monorepo_v2/backend/migrations/versions/a3683ddb987c_init.py
monorepo_v2/backend/migrations/versions/a5d3661ccee5_add_size_and_sha256_columns_to_artifacts.py
monorepo_v2/backend/migrations/versions/ba37eabeee95_fix_artifact_model.py
monorepo_v2/backend/migrations/versions/bd142ee8c0ea_initial_migration.py

## Posibles secretos/artefactos
- .env en árbol:
forge_saas/.env
backup_repo_a/backup_repo/forge_saas/.env
backup_repo_a/backup_repo/.env
backup_repo_a/forge_saas/.env
backup_repo_a/.env
- .env-like:
.env
forge_saas/.env
- Artefactos (zip/tar):
forge_saas/forge_saas_backup_20250917_164711.tar.gz
forge_saas/generated/28bdea12-fae6-4d4a-80a7-a193d8457e0e.zip
