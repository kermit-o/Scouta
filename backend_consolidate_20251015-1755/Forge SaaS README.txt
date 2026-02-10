Perfecto, cambio registrado: **adiós Streamlit, hola Next.js/React** como UI principal de Forge SaaS.
Te genero los **4 documentos** ya adaptados a esta realidad.

---

## 📄 1) `docs/forge_saas_modules.md`

```markdown
# Forge SaaS — Catálogo de Módulos (Lego System)

> Versión: 2025-11-18  
> UI oficial: **Frontend Next.js/React**  
> Backend: **FastAPI + Postgres**

Este documento define los **módulos reutilizables** de Forge SaaS.  
Cada proyecto generado (ecommerce, viajes, blog, etc.) es una combinación de estos bloques.

---

## 1. Categorías de módulos

1. **Core de plataforma**
2. **Dominio de negocio** (ecommerce, viajes, blog, LMS, etc.)
3. **Infraestructura & DevEx**
4. **IA & Orquestación**

Cada módulo expone:

- **Backend**: rutas FastAPI, modelos SQLAlchemy, schemas Pydantic, servicios.
- **Frontend**: componentes Next.js/React reutilizables (páginas, layouts, hooks).
- **Config**: entradas en `.env`, `docker-compose`, permisos, roles.

---

## 2. Módulos Core de Plataforma

### 2.1. Auth & Users (`core_auth_users`) — [MVP]

- **Responsabilidad**:
  - Registro / login
  - Tokens JWT
  - Gestión de usuarios básicos

- **Backend**:
  - Rutas:
    - `POST /api/auth/register`
    - `POST /api/auth/login`
    - `GET /api/auth/me`
  - Tablas:
    - `users`
    - `refresh_tokens` (fase posterior)
  - Esquemas:
    - `UserCreate`, `UserLogin`, `UserOut`

- **Frontend (Next.js)**:
  - Páginas:
    - `/auth/login`
    - `/auth/register`
  - Componentes:
    - `<AuthForm />`
    - `<ProtectedRoute />`

- **Depende de**:
  - `core_config`
  - `core_database`

---

### 2.2. Projects (`core_projects`) — [EXISTENTE]

- **Responsabilidad**:
  - Representar un “proyecto generado” en Forge
  - Guardar requirements, plan, artefactos

- **Backend**:
  - Modelo `Project`:
    - `id, name, status, requirements, plan_json, generated_plan,
       technology_stack, result, artifact_path,
       created_at, updated_at`
  - Rutas actuales:
    - `/api/projects` (listar, crear)
    - `/api/projects/{id}` (detalles)
    - `/artifact/{id}` (descarga ZIP)

- **Frontend (Next.js)**:
  - Páginas:
    - `/projects`
    - `/projects/[id]`
  - Componentes:
    - `<ProjectCard />`
    - `<ProjectStatus />`
    - `<ArtifactDownloadButton />`

---

### 2.3. Billing & Plans (`core_billing`) — [PLANNED]

- **Responsabilidad**:
  - Planes de suscripción (Free / Pro / Enterprise)
  - Límites de generación

- **Backend**:
  - Modelos:
    - `Plan`, `Subscription`, `UsageQuota`
  - Integración:
    - Stripe para pagos
  - Rutas:
    - `/api/billing/plans`
    - `/api/billing/subscriptions`
    - `/api/billing/usage`

- **Frontend**:
  - Página `/pricing`
  - Componente `<PlanSelector />`
  - Integración con módulo `payments_stripe`

---

### 2.4. Payments (Stripe) (`core_payments_stripe`) — [PLANNED]

- **Responsabilidad**:
  - Crear sesiones de checkout
  - Webhooks de Stripe
  - Asociar suscripción a usuario

- **Backend**:
  - Rutas:
    - `POST /api/payments/create-checkout-session`
    - `POST /api/payments/webhooks/stripe`
  - Usa `stripe` SDK + `STRIPE_SECRET_KEY`

- **Frontend**:
  - Botón “Upgrade to Pro” → redirige a Checkout
  - Página de éxito/cancelación:
    - `/billing/success`
    - `/billing/cancel`

---

### 2.5. Notifications (`core_notifications`) — [FUTURE]

- Email (SendGrid / SMTP)
- Webhooks externos
- Posiblemente Telegram / Slack

---

## 3. Módulos de Dominio de Negocio

### 3.1. Ecommerce (`domain_ecommerce`) — [EN DISEÑO]

- **Responsabilidad**:
  - Catálogo de productos
  - Carrito
  - Órdenes
  - Métodos de pago (conecta con `core_payments_stripe`)

- **Backend**:
  - Tablas:
    - `products`, `categories`, `orders`, `order_items`
  - Rutas:
    - `/api/products/*`
    - `/api/orders/*`

- **Frontend (Next.js)**:
  - Páginas:
    - `/shop`
    - `/products/[id]`
    - `/cart`
    - `/checkout`
  - Componentes básicos:
    - `<ProductCard />`
    - `<CartDrawer />`
    - `<CheckoutForm />`

---

### 3.2. Travel / Booking (`domain_travel`) — [PLANNED]

- **Responsabilidad**:
  - Destinos
  - Disponibilidad
  - Reservas
  - Pagos

Parte reutilizable de ecommerce:

- Users / Auth
- Payments
- Landing
- Booking (similar a orders)

---

### 3.3. Blog / CMS (`domain_blog`) — [PLANNED]

- Posts, categorías, etiquetas, comentarios
- SEO básico

---

### 3.4. Otros módulos (solo listados)

- `domain_lms` (cursos, lecciones, progresos)
- `domain_marketplace` (multi-vendor)
- `domain_inventory` (stock avanzado)
- `domain_dashboard` (panel admin con métricas)

---

## 4. Módulos de Infraestructura & DevEx

- `infra_logging` — Logging estructurado
- `infra_monitoring` — métricas, health checks avanzados
- `infra_task_queue` — colas (Celery / RQ) [solo plan]
- `infra_scaffolding` — helpers para generar código, trees, ficheros

---

## 5. Módulos de IA & Orquestación

### 5.1. Planning Agent (`ai_planning_agent`) — [PLANNED]

- Analiza requirements
- Saca:
  - lista de módulos
  - tech stack
  - tareas de implementación

### 5.2. Builder Agent (`ai_builder_agent`) — [PLANNED]

- Rellena templates con código
- Ajusta modelos, rutas, servicios
- Genera artefactos (backend + opcionalmente UI Next.js)

### 5.3. Analyzer (`ai_analyzer`) — [FUTURE]

- Analiza proyectos existentes
- Sugiere mejoras, migraciones, refactors

---

## 6. Convenciones de Módulos

- Nombre de módulo: `tipo_nombre` (ej: `domain_ecommerce`)
- Cada módulo define:
  - `module.yml` (metadatos)
  - `backend/` (routes, models, services)
  - `frontend/` (páginas Next.js, componentes)
- El pipeline central compone módulos con base en:
  - requirements
  - plan del PlanningAgent
  - plantilla base seleccionada
```

---

## 📄 2) `docs/forge_saas_templates.md`

````markdown
# Forge SaaS — Sistema de Plantillas

> Backend: FastAPI + Postgres  
> Frontend target: Next.js/React (UI externa, no Streamlit)

---

## 1. ¿Qué es una plantilla en Forge SaaS?

Una **plantilla** es un “esqueleto ejecutable” que define:

- Estructura de carpetas
- Dependencias (`requirements.txt`, `pyproject.toml`)
- Modelo de datos mínimo
- Conjunto inicial de rutas
- Configuración Docker
- Opcionalmente, una semilla de UI (Next.js) en el futuro

Cada plantilla vive bajo:

```bash
templates/
  <template_name>/
    PLAN/plan.json
    backend/
    ui/              # (para Next.js, futuro)
    alembic/
    docker-compose.yml
    ...
````

---

## 2. Plantilla base actual

### 2.1. `forge_fastapi_pg_crud_v1` — [READY]

Ruta:

```bash
templates/forge_fastapi_pg_crud_v1/
```

Contenido (simplificado):

* `backend/`:

  * `app/main.py` (FastAPI)
  * `app/db.py` (SQLAlchemy engine & Session)
  * `app/models.py` (User)
  * `app/schemas.py` (UserCreate, UserOut)
  * `app/routers/health.py`
  * `app/routers/users.py`
  * `app/requirements.txt`
* `alembic/`, `alembic.ini`:

  * Migración `0001_init.py` con tabla `users`
* `docker-compose.yml`:

  * Servicio `api` y `db` (en esta plantilla o ajustable)
* `PLAN/plan.json`:

  * Describe pasos generados originalmente

Esta plantilla se ha demostrado **ejecutable y estable**:

* `/api/health` OK
* `/api/users/`:

  * GET lista
  * POST crea usuario y lo persiste

Se usa como **semilla** para:

* CRUD genéricos
* Prototipos de backend simples
* Base para módulos de dominio

---

## 3. Plantillas planeadas

### 3.1. `forge_fastapi_pg_ecommerce_v1` — [PLANNED]

Objetivo:

* Backend completo de ecommerce:

  * `products`, `categories`, `orders`, `order_items`
* Integración con:

  * `core_auth_users`
  * `domain_ecommerce`
  * `core_payments_stripe` (en fases posteriores)

Estructura:

```bash
templates/forge_fastapi_pg_ecommerce_v1/
  backend/
    app/main.py
    app/core/
    app/api/
    app/models/
    app/schemas/
    app/services/
    app/repositories/
  alembic/
  docker-compose.yml
  PLAN/plan.json
  ui/ (futuro: Next.js)
```

---

### 3.2. `forge_fastapi_pg_travel_v1` — [DRAFT]

* Basada en:

  * `core_auth_users`
  * `domain_travel`
  * `core_payments_stripe`
* Modelos:

  * `destinations`, `bookings`, `payments`

---

### 3.3. `forge_fastapi_pg_blog_v1` — [DRAFT]

* Basada en:

  * `core_auth_users`
  * `domain_blog`
* Modelos:

  * `posts`, `categories`, `comments`

---

### 3.4. `forge_fastapi_pg_lms_v1` — [FUTURE]

* Cursos, lecciones, progreso, quizzes

---

## 4. Relación Plantilla ↔ Módulos

Ejemplo (ecommerce):

```yaml
template: forge_fastapi_pg_ecommerce_v1
modules:
  - core_auth_users
  - core_projects
  - core_payments_stripe
  - domain_ecommerce
  - infra_logging
```

Ejemplo (travel):

```yaml
template: forge_fastapi_pg_travel_v1
modules:
  - core_auth_users
  - core_projects
  - core_payments_stripe
  - domain_travel
  - infra_logging
```

---

## 5. Evolución con Next.js (sin Streamlit)

* La UI ya **no** será Streamlit.
* Cada template podrá incluir una carpeta:

```bash
templates/<template_name>/ui/
  next/
    package.json
    app/
    components/
    lib/
```

* Forge podrá:

  * Generar solo backend
  * Generar backend + estructura Next.js básica
  * O dejar hooks claros para que el usuario conecte su propio Next.js

---

## 6. Convenciones

* Nombre de plantilla:

  * `forge_<stack>_<dominio>_v<major>`
  * Ej: `forge_fastapi_pg_ecommerce_v1`
* Documentar cada plantilla en:

  * `docs/templates/<template_name>.md`
* Cada plantilla debe:

  * Levantar con `docker compose up`
  * Exponer `/api/health`
  * Tener al menos un recurso CRUD completo

````

---

## 📄 3) `docs/forge_saas_pipeline.md`

```markdown
# Forge SaaS — Pipeline de Generación

> Desde el prompt del usuario hasta un proyecto ejecutable  
> Backend: FastAPI / Python  
> UI consumidora: Next.js/React

---

## 1. Vista general

Flujo completo:

1. Usuario describe proyecto (UI Next.js)
2. Request → Backend `/api/projects`
3. Planning:
   - mínimo (actual)
   - IA (futuro, PlanningAgent)
4. Selección de plantilla + módulos
5. Generación de artefactos (backend y opcionalmente UI)
6. Packaging (ZIP)
7. Descarga / clonación

---

## 2. Paso a paso (versión actual)

### Paso 0 — Entorno

- Docker Compose levanta:
  - `backend` (Forge API)
  - `db` (Postgres)
  - `ui` (en el futuro: Next.js; por ahora la UI antigua era Streamlit)

---

### Paso 1 — Creación de Proyecto

**Endpoint:**

```http
POST /api/projects
Content-Type: application/json
````

**Body (simplificado):**

```json
{
  "name": "Mi E-commerce Demo",
  "requirements": {
    "stack": "fastapi_pg_ecommerce",
    "features": ["ecommerce","products_crud","orders","postgres","alembic"],
    "variables": {
      "python_version": "3.12",
      "service_name": "ecommerce-app"
    }
  }
}
```

El backend:

* Crea un `Project` en la BD
* Devuelve `project_id`
* Estado inicial: `status = "queued" | "pending"`

---

### Paso 2 — Planning mínimo

Actualmente:

* Lógica Python simple (no IA “gorda” todavía)
* Genera un plan estructurado (JSON) basado en:

  * `requirements.stack`
  * `requirements.features`

Resultado:

* Se rellena `Project.plan_json`
* Se inicializa `generated_plan` con tareas básicas

---

### Paso 3 — Selección de plantilla

Basado en `requirements.stack`, por ejemplo:

* `fastapi_pg_crud` → `forge_fastapi_pg_crud_v1`
* `fastapi_pg_ecommerce` → `forge_fastapi_pg_ecommerce_v1` (cuando esté lista)
* `fastapi_pg_travel` → `forge_fastapi_pg_travel_v1` (futuro)

---

### Paso 4 — Generación de Artefactos

El generador:

1. Copia la plantilla a un `workdir` único:

   * `backend_reorganized/workdir/<project_uuid>/`
2. Aplica transformaciones:

   * rename de paquetes
   * ajustes en modelos
   * cambios en textos (`project_name`, etc.)
3. Guarda la salida en disco:

   * código backend completo
   * archivos de infra (`docker-compose.yml`, `alembic.ini`)

---

### Paso 5 — Packaging (ZIP)

* Se comprime el `workdir` en un `.zip`
* Ruta guardada en `Project.artifact_path`
* `Project.status` → `"generated"`

---

### Paso 6 — Descarga

Endpoint:

```http
GET /artifact/{project_id}
```

* La UI Next.js descargará este ZIP
* El usuario puede:

  * descomprimir localmente
  * abrir en Codespaces
  * o incluirlo en su propio monorepo

---

## 3. Pipeline objetivo (con IA + Next.js)

### 3.1. Intake & Understanding (IA)

* Endpoint inicial igual (`POST /api/projects`)
* PlanningAgent:

  * Detecta tipo de proyecto:

    * ecommerce, travel, blog, LMS…
  * Propone:

    * módulos necesarios
    * plantilla base más cercana
    * tech stack extendido

---

### 3.2. Module Graph

* IA construye un “grafo de módulos”:

```json
{
  "template": "forge_fastapi_pg_ecommerce_v1",
  "modules": [
    "core_auth_users",
    "core_projects",
    "core_payments_stripe",
    "domain_ecommerce",
    "infra_logging"
  ]
}
```

---

### 3.3. GenerationAgent (backend + UI)

* Backend:

  * une módulos
  * ajusta modelos, rutas, servicios
* UI (Next.js):

  * crea páginas base
  * crea componentes por módulo:

    * `/shop`, `/products/[id]`, `/checkout`
    * `/auth/login`, `/auth/register`, etc.

---

### 3.4. Post-procesado

* Validación de imports
* Chequeos:

  * `/api/health`
  * migraciones DB
* Opcional: ejecutar tests básicos

---

## 4. Jobs y progreso

Para operaciones más largas:

* Se usa un `job_id` separado de `project_id`
* Endpoints tipo:

```http
POST /api/projects/{project_id}/plan
POST /api/projects/{project_id}/generate
GET  /api/progress/{job_id}
```

`progress` contiene:

```json
{
  "job_id": "uuid",
  "percent": 80,
  "message": "Empaquetando proyecto...",
  "updated_at": "2025-11-18T04:17:00Z"
}
```

La UI Next.js puede mostrar una barra de progreso en tiempo real.

---

## 5. Principios del pipeline

* **Idempotente**: repetir un job no corrompe datos.
* **Observabilidad**: logs claros por etapa (Intake, Plan, Generate, Package).
* **Separación de preocupaciones**:

  * Backend genera artefactos
  * Next.js solo orquesta y visualiza
* **Reproducible**:

  * mismo input → mismo output (en modo determinista)

````

---

## 📄 4) `docs/forge_saas_roadmap.md`

```markdown
# Forge SaaS — Roadmap Oficial

> Backend: FastAPI + Postgres  
> Frontend: Next.js/React (UI principal)  
> Filosofía: Módulos tipo Lego + Plantillas + IA

---

## 1. Estructura de hitos

Tres grandes hitos:

- **Hito A** — Arranca y planifica
- **Hito B** — Usable y mantenible (para usuarios reales)
- **Hito C** — IA real y generación avanzada

---

## 2. Hito A — “Arranca y Planifica” ✅ ~90%

### Objetivo

Tener un sistema que:

- Levante con Docker (backend + db)
- Registre proyectos
- Genere un proyecto base
- Empaquete artefactos en ZIP
- Exponga `/api/health` estable

### Estado

- ✅ Backend FastAPI arranca
- ✅ Postgres estable (`uuid-ossp`, search_path, DATABASE_URL)
- ✅ Modelo `Project` implementado
- ✅ Generador minimal → ZIP funcional (CRUD demo)
- ✅ Plantilla `forge_fastapi_pg_crud_v1` validada
- ✅ Flujo: create project → plan mínimo → generar → artefacto
- ❌ UI aún está en transición (Streamlit → Next.js)
- ❌ Stripe / billing no estabilizados (baja prioridad inmediata)

---

## 3. Hito B — “Usable y Mantenible” 🚧 (Siguiente fase)

### Objetivo

Convertir Forge SaaS en un producto **usado por humanos** sin tocar código interno.

### 3.1. Backend

- [ ] Añadir endpoints limpios para:
  - `POST /api/projects` (crear)
  - `POST /api/projects/{id}/plan`
  - `POST /api/projects/{id}/generate`
  - `GET  /api/projects/{id}`
  - `GET  /api/projects`
  - `GET  /artifact/{id}`
- [ ] Definir errores consistentes (schemas de error)
- [ ] Logging estructurado
- [ ] Config centralizada (settings)

### 3.2. UI Next.js

- [ ] App Next.js dedicada:

  - `/` → landing de Forge SaaS
  - `/projects` → lista de proyectos
  - `/projects/new` → wizard de creación (stack, tipo de negocio, etc.)
  - `/projects/[id]` → detalle, progreso, descarga

- [ ] Integración con API:
  - Fetch con `fetch` o `react-query`/`SWR`
  - Progreso en tiempo real vía pooling simple (y luego WebSocket si quieres)

- [ ] Estilo:
  - Tailwind + algún kit (shadcn/ui, etc.)
  - Diseño tipo Lovable (limpio, moderno, claro)

### 3.3. Plantillas adicionales

- [ ] `forge_fastapi_pg_ecommerce_v1`
- [ ] `forge_fastapi_pg_travel_v1`
- [ ] `forge_fastapi_pg_blog_v1`

Cada una:

- Debe levantar por sí misma
- Tener al menos un dominio bien resuelto:
  - productos/órdenes
  - reservas
  - posts/comentarios

### 3.4. Calidad / DX

- [ ] Tests unitarios básicos (Project, generator)
- [ ] Tests de integración (generar y verificar estructura mínima)
- [ ] Scripts de diagnóstico claros:
  - `scripts/diagnostics_backend.sh`
  - `scripts/diagnostics_templates.sh`

---

## 4. Hito C — “IA Real & Generación Avanzada” 🧠

### Objetivo

Que Forge pueda:

- Entender prompts complejos de usuario
- Proponer arquitectura / módulos
- Generar proyectos más sofisticados que simples CRUD

### 4.1. PlanningAgent

- [ ] Integra modelo LLM (DeepSeek / OpenAI / otro)
- [ ] Toma:
  - descripción libre del usuario
- [ ] Devuelve:
  - tipo de negocio
  - módulos recomendados
  - plantilla base
  - tech stack sugerido
  - posibles riesgos/complejidad

### 4.2. BuilderAgent

- [ ] Rellena plantillas backend:
  - modelos
  - rutas
  - servicios
- [ ] En una segunda fase:
  - genera también esqueletos Next.js:
    - páginas, layouts, formularios

### 4.3. Evolución a “plataforma de módulos”

- [ ] Repositorio central de módulos:
  - `core`, `domain`, `infra`, `ai`
- [ ] Marketplace interno (futuro):
  - poder añadir módulos de terceros

---

## 5. Qué NO vamos a hacer (por ahora)

Para mantener el foco:

- ❌ No convertir Forge en un IDE online completo
- ❌ No intentar soportar todos los stacks del mundo (de momento: FastAPI + Next.js)
- ❌ No hacer workflows visuales ultra complejos antes de estabilizar:
  - backend
  - plantillas
  - pipeline

---

## 6. Resumen de prioridades

### Ahora (tú, Outman, próximo sprint):

1. Consolidar documentación (hecho con estos 4 archivos).
2. Diseñar la UI de Forge en Next.js (wireframes y primeras rutas).
3. Conectar Next.js con el backend actual (mínimo CRUD de Projects + descarga artefacto).
4. Extraer una plantilla ecommerce “de verdad” a partir de lo que ya probaste.

### Después:

5. Añadir más plantillas de dominio.
6. Integrar PlanningAgent.
7. Potenciar BuilderAgent.

---
````

---

Si quieres, en el siguiente paso puedo:

* Proponerte la **estructura exacta del repo frontend Next.js** para Forge (carpetas, páginas, componentes base).
* O diseñar el **API contract** entre Next.js y el backend (tipos, endpoints, errores) para que el UI sea tan fluido como Lovable.
