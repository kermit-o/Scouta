# Scouta — Roadmap y Workflow de Lanzamiento a App Store y Google Play

> Documento de planificación estilo agencia (metodología tipo **Appinventiv / ScienceSoft**: *discovery-led*, Agile/Scrum por *pods*, workstreams paralelos, *quality gates* y *release management* formal).
>
> **Versión:** 1.0 · **Fecha:** 2026-05-26 · **Estado:** Propuesta para aprobación · **Owner:** Delivery Lead

---

## 0. Cómo aborda esto un equipo de agencia

Una agencia no “sube la app y ya”. Trabaja en **5 disciplinas en paralelo** bajo un *delivery manager*, con *gates* de calidad entre fases y un *compliance officer* que valida requisitos de tienda **antes** de escribir código. El principio rector: **el camino crítico es Pagos (IAP/Play Billing) + Trust & Safety + borrado de cuenta**, no la UI. Todo lo demás se planifica alrededor de ese camino crítico.

Marco de entrega:
- **Cadencia:** Sprints de 2 semanas, *daily standup*, *sprint review* + *retro*, *backlog grooming* semanal.
- **Gestión:** Jira (epics = workstreams), Confluence (specs), tablero de *release readiness*.
- **Gobernanza:** *Weekly Status Report* a stakeholders + *RAG status* (Red/Amber/Green) por workstream.
- **Definition of Ready / Definition of Done** explícitas por historia.

---

## 1. Resumen ejecutivo y estado actual

**Producto:** Scouta — red social + *live streaming* (LiveKit) con chat, regalos y economía de monedas; disponible en **web (Next.js)** y **móvil (Expo / React Native)**.

**Estado actual (assessment):**

| Área | Estado | Nota |
|------|--------|------|
| Funcionalidad core (live, chat, regalos, perfiles) | 🟢 Madura | Web + móvil funcionando; bugs en pulido (p. ej. end-screen) |
| Pagos de monedas | 🔴 **Bloqueante** | Vía **Stripe Checkout** — prohibido para bienes digitales en apps nativas |
| Trust & Safety (report/block/moderación) | 🟠 Parcial | Existe *block* de host en live; falta *report*, block a nivel cuenta, moderación |
| Borrado de cuenta in-app | 🔴 Requerido | Obligatorio en Apple y Google |
| Privacidad / legales | 🟠 Parcial | Falta Privacy Labels, Data Safety, EULA UGC |
| Estabilidad / QA | 🟠 En progreso | Distribución por APK/OTA; sin matriz de dispositivos formal |
| Release engineering móvil | 🟠 Parcial | EAS/OTA en uso; falta pipeline de store builds + signing gestionado |

**Veredicto:** No listo para *submission* inmediata. **Estimación realista: 8–10 semanas** (camino crítico = Pagos) hasta un envío con alta probabilidad de aprobación, ejecutando beta cerrada en paralelo desde la semana 1.

---

## 2. Objetivos y criterios de éxito (Launch Readiness Definition)

Se considera **“Ready to Submit”** cuando **todos** estos criterios están en verde:

1. Monedas/regalos comprables vía **Apple IAP** y **Google Play Billing** (Stripe solo en web).
2. Flujo de **report** de usuario/contenido + **block** a nivel cuenta + **borrado de cuenta** in-app.
3. Política de moderación documentada + SLA de actuación ≤24h + filtro de contenido objetable.
4. **Privacy Policy** publicada + **Privacy Nutrition Labels** (Apple) + **Data Safety** (Google) completos.
5. **EULA / Terms** con cláusula de tolerancia cero a UGC abusivo, aceptados en *onboarding*.
6. Crash-free sessions **≥ 99.5%** en beta; 0 *blocker/critical* abiertos.
7. Builds firmados reproducibles desde CI (EAS) con *versioning* automatizado.
8. *Store listing* completo (ASO, screenshots, vídeo, descripciones) + cuentas demo para revisores.
9. *Target API level* de Google y *minimum iOS* alineados a los requisitos vigentes de la tienda.
10. Aprobación formal del *Compliance Gate* y del *Go/No-Go* de stakeholders.

---

## 3. Composición del equipo (pod)

| Rol | Dedicación | Responsabilidad principal |
|-----|-----------|---------------------------|
| Delivery Manager / Scrum Master | 50% | Plan, riesgos, ceremonias, reporting |
| Product Owner | 50% | Backlog, prioridad, *acceptance* |
| Tech Lead (Mobile) | 100% | Arquitectura móvil, IAP, release eng. |
| iOS/Android Engineer(s) (RN/Expo) | 2 × 100% | Implementación móvil |
| Backend Engineer | 100% | IAP webhooks, moderación, borrado cuenta, escalado |
| QA Engineer (manual + automation) | 100% | Estrategia de test, matriz de dispositivos, *store pre-checks* |
| Compliance / Trust & Safety Specialist | 50% | Requisitos Apple/Google, privacidad, políticas |
| UX/UI Designer | 50% | Flujos de IAP/report/borrado, *store assets* |
| DevOps | 30% | CI/CD (EAS), observabilidad, *secrets* |
| ASO / Growth | 25% | *Listing*, keywords, plan de *rollout* |

---

## 4. Workstreams (tracks paralelos)

| ID | Workstream | Prioridad | Owner |
|----|-----------|-----------|-------|
| **WS1** | Pagos: IAP + Play Billing (camino crítico) | P0 | Tech Lead + Backend |
| **WS2** | Trust & Safety / UGC (report, block, moderación) | P0 | Backend + Compliance |
| **WS3** | Privacidad & Legal (labels, data safety, EULA, borrado cuenta) | P0 | Compliance + Backend |
| **WS4** | Release Engineering móvil (EAS, signing, versioning) | P1 | DevOps + Tech Lead |
| **WS5** | QA & Test Strategy | P1 | QA |
| **WS6** | Backend Readiness (escalado, observabilidad) | P1 | Backend + DevOps |
| **WS7** | Store Presence / ASO / Assets | P2 | ASO + Designer |
| **WS8** | Analytics & Growth instrumentation | P2 | Mobile + Growth |

---

## 5. Roadmap por fases

| Fase | Duración | Objetivo | Gate de salida |
|------|----------|----------|----------------|
| **F0 — Discovery & Compliance Audit** | Sem. 1–2 | Mapear requisitos exactos de tienda, *gap analysis*, specs | **Compliance Gate 1**: backlog de cumplimiento aprobado |
| **F1 — Beta cerrada (paralelo)** | Sem. 1–8 | TestFlight + Play Internal Testing para feedback y estabilidad | ≥12 testers / 14 días (req. Google) |
| **F2 — Build: Pagos + T&S + Privacidad** | Sem. 2–6 | Implementar P0 (IAP, report/block, borrado, labels) | **Feature Complete Gate** |
| **F3 — Hardening & QA** | Sem. 6–8 | Estabilidad, matriz de dispositivos, regresión, perf | **Quality Gate**: crash-free ≥99.5%, 0 blockers |
| **F4 — Store Readiness** | Sem. 7–8 | Assets, ASO, cuentas demo, formularios de privacidad | **Submission Gate** (Go/No-Go) |
| **F5 — Submission & Review** | Sem. 8–10 | Envío a Apple/Google, responder a *review* | App aprobada |
| **F6 — Launch & Post-launch** | Sem. 10+ | *Phased rollout*, monitorización, *hotfix* readiness | KPIs estables |

---

## 6. Plan de sprints (2 semanas c/u)

**Sprint 1 (Sem 1–2) — Discovery + cimientos**
- Auditoría de cumplimiento Apple/Google (checklist completo).
- Setup TestFlight + Play Internal Testing; subir build actual a beta.
- Spike IAP: catálogo de productos de monedas (SKUs), arquitectura de webhooks.
- Diseño UX de: compra de monedas (IAP), *report*, borrado de cuenta.
- *Gap analysis* documentado en Confluence.

**Sprint 2 (Sem 3–4) — Pagos (core) + T&S (inicio)**
- IAP iOS (StoreKit) y Play Billing: compra, validación de recibo *server-side*, acreditación en wallet.
- Endpoints backend: verificación de recibos Apple/Google + idempotencia.
- *Report* de usuario/contenido (UI + API + cola de moderación básica).
- Block a nivel de cuenta.

**Sprint 3 (Sem 5–6) — Pagos (cierre) + Privacidad**
- Restauración de compras, manejo de *refunds*/reembolsos, estados de error.
- Borrado de cuenta in-app (flujo + borrado/anonimizado backend + *grace period*).
- Privacy Policy + EULA (UGC) + aceptación en onboarding.
- Privacy Nutrition Labels + Data Safety form (borradores).
- **Gate: Feature Complete.**

**Sprint 4 (Sem 7–8) — Hardening + Store Readiness**
- Matriz de dispositivos + regresión completa; pruebas de IAP en sandbox.
- Perf (arranque, memoria en live, reconexión), accesibilidad básica.
- Store assets, screenshots, vídeo, descripciones, ASO.
- Cuentas demo + notas para revisores (cómo probar un live).
- **Gate: Quality + Submission (Go/No-Go).**

**Sprint 5 (Sem 9–10) — Submission + Launch**
- Envío a ambas tiendas; gestión de *review* y respuestas a rechazos.
- *Phased rollout* en Google (5%→20%→...); release controlado en Apple.
- Monitorización (Crashlytics/Sentry), *war room* de lanzamiento.

---

## 7. Matriz RACI (resumida)

| Actividad | PO | Tech Lead | Backend | QA | Compliance | DevOps |
|-----------|----|-----------|---------|----|------------|--------|
| IAP / Play Billing | A | R | R | C | C | C |
| Verificación de recibos (server) | C | C | R/A | C | I | C |
| Report / Block / Moderación | A | C | R | C | R | I |
| Borrado de cuenta | A | C | R | C | R | I |
| Privacy Labels / Data Safety | C | I | C | I | R/A | I |
| Pipeline EAS / signing | I | A | I | I | I | R |
| Estrategia de QA | C | C | C | R/A | C | C |
| Store listing / ASO | A | I | I | I | C | I |
| Go/No-Go submission | A | C | C | C | R | C |

*(R=Responsable, A=Aprobador, C=Consultado, I=Informado)*

---

## 8. Detalle por workstream (tareas + Definition of Done)

### WS1 — Pagos (IAP + Play Billing) — CAMINO CRÍTICO
**Por qué:** Apple Guideline 3.1.1 y la política de Google exigen que los **bienes digitales** (monedas, regalos) se compren con **IAP / Play Billing**. El Stripe actual solo es válido en **web**. La app debe detectar plataforma y usar el método correcto.

Tareas:
- Definir catálogo de monedas como **productos consumibles** (SKUs) en App Store Connect y Play Console.
- Integrar **StoreKit 2** (iOS) y **Google Play Billing** (Android) en el cliente Expo (p. ej. `react-native-iap` / `expo-in-app-purchases` o módulo nativo).
- **Verificación de recibos server-side** (App Store Server API / Google Play Developer API) — nunca confiar en el cliente.
- Acreditar monedas con **idempotencia** y *audit log*; reconciliación con el wallet existente.
- *Restore purchases*, manejo de *pending/deferred*, *refund notifications* (Apple/Google webhooks).
- Mantener Stripe **solo** en el flujo web.

**DoD:** compra real en sandbox acredita monedas; recibos verificados en servidor; *restore* funciona; no hay ruta de compra de bienes digitales fuera de IAP en móvil.

### WS2 — Trust & Safety / UGC
Tareas:
- **Report** de usuario, live, mensaje y perfil (UI + API + cola de moderación).
- **Block** a nivel de cuenta (no solo en el live actual).
- Panel/cola de moderación + SLA de actuación ≤24h; *takedown* de contenido.
- Filtro de contenido objetable (palabras + reportes); *rate limiting* de chat.
- *Kill switch* para terminar un live abusivo (admin).

**DoD:** un usuario puede reportar y bloquear; el equipo puede actuar y eliminar; documentado en política.

### WS3 — Privacidad & Legal
Tareas:
- **Borrado de cuenta in-app** (obligatorio): flujo claro + borrado/anonimizado en backend + manejo de datos asociados (lives, pagos, wallet).
- **Privacy Policy** y **EULA** con cláusula de tolerancia cero a UGC abusivo; aceptación en onboarding.
- **Privacy Nutrition Labels** (Apple) y **Data Safety form** (Google) coherentes con los datos reales recolectados.
- Consentimiento de permisos (cámara/micro) con textos de uso (`NSCameraUsageDescription`, etc.).
- GDPR/locales: derecho de acceso/borrado, retención de datos.

**DoD:** borrado de cuenta operativo end-to-end; formularios completos y veraces; documentos publicados y enlazados.

### WS4 — Release Engineering móvil
Tareas:
- Pipeline **EAS Build** para builds de store (iOS .ipa / Android .aab) + **EAS Submit**.
- Gestión de *signing* (certificados Apple, *keystore* Android) y *secrets*.
- *Versioning* automatizado (semver + build number) y *changelogs*.
- Separar canales: OTA para JS, *store build* para nativo; política de OTA conforme a tiendas.
- *Target API level* Android y *deployment target* iOS al día.

**DoD:** un *tag* dispara build firmado reproducible subible a TestFlight/Play.

### WS5 — QA & Test Strategy
Tareas:
- **Test pyramid**: unit (Jest), componente, E2E (Detox/Maestro), manual exploratorio.
- **Matriz de dispositivos** (gama alta/media/baja iOS+Android, tamaños, OS versions).
- Casos críticos: live (host/viewer), reconexión, IAP sandbox, report/block, borrado de cuenta, *deep links*.
- *Store pre-submission checks* (Apple/Google guidelines como checklist).
- Pruebas de red degradada, *background/foreground*, permisos denegados.

**DoD:** suite de regresión verde; crash-free ≥99.5% en beta; 0 *blocker/critical*.

### WS6 — Backend Readiness
Tareas:
- Escalado de LiveKit y API para picos de lanzamiento; *load test*.
- Observabilidad: logs estructurados, métricas, *tracing*, alertas.
- Webhooks IAP/Play robustos (reintentos, *dead-letter*).
- *Rate limiting*, abuso, *secrets* rotados.

**DoD:** *runbook* operativo + dashboards + alertas; *load test* aprobado.

### WS7 — Store Presence / ASO
Tareas:
- Iconos, screenshots por tamaño, *preview video*, descripciones (corta/larga), keywords.
- **Age rating** (probable 17+ por streaming con desconocidos) en ambos cuestionarios.
- Localización mínima (ES/EN).
- *App Privacy* y categorías correctas.

**DoD:** *listing* 100% completo en App Store Connect y Play Console.

### WS8 — Analytics & Growth
Tareas:
- Eventos clave (registro, primer live, compra de monedas, follow, retención).
- *Attribution* y *funnels*; consentimiento de *tracking* (ATT en iOS).
- Dashboards de KPIs de lanzamiento.

**DoD:** eventos validados en QA; ATT prompt conforme a Apple.

---

## 9. Quality Gates (criterios de entrada/salida)

| Gate | Criterio |
|------|----------|
| **Compliance Gate 1** (fin F0) | *Gap analysis* completo; backlog P0 aprobado; SKUs definidos |
| **Feature Complete** (fin Sprint 3) | IAP + report/block + borrado de cuenta + privacidad implementados |
| **Quality Gate** (fin Sprint 4) | crash-free ≥99.5%; regresión verde; IAP sandbox OK; 0 blockers |
| **Submission Gate** (Go/No-Go) | *Listing* completo; cuentas demo; formularios; aprobación stakeholders |
| **Launch Gate** | Aprobado por tiendas; monitorización activa; *rollback* listo |

---

## 10. Risk Register

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|--------|-------|---------|------------|
| R1 | Rechazo de Apple por usar Stripe para monedas (3.1.1) | Alta | Crítico | IAP obligatorio antes de submit; QA en sandbox |
| R2 | Rechazo por UGC sin report/moderación (1.2) | Alta | Crítico | WS2 como P0; documentar política |
| R3 | Falta de borrado de cuenta | Media | Alto | WS3 prioritario; QA end-to-end |
| R4 | Comisión 15–30% afecta *unit economics* | Alta | Alto | Modelar precios; *Small Business Program* (Apple 15%) |
| R5 | Inestabilidad en dispositivos de gama baja | Media | Alto | Matriz de dispositivos; perf budget |
| R6 | Política OTA (Expo Updates) vs reglas de tienda | Media | Medio | OTA solo JS/bugfix, no cambios sustanciales de features |
| R7 | Privacy Labels inexactos → rechazo/retirada | Media | Alto | Compliance audita datos reales |
| R8 | Requisito Google de closed testing (12 testers/14d) retrasa | Media | Medio | Iniciar beta en Sprint 1 |
| R9 | Ciclos de rechazo de Apple alargan timeline | Alta | Medio | Presupuestar 1–2 ciclos; *expedited review* si aplica |
| R10 | Escalado LiveKit en pico de lanzamiento | Media | Alto | *Load test* + rollout faseado |

---

## 11. Checklist de submission — Apple App Store

- [ ] Cuenta Apple Developer activa + *agreements* y *banking/tax* completos.
- [ ] Bienes digitales vía **In-App Purchase** (consumibles de monedas).
- [ ] **Account deletion** in-app.
- [ ] UGC: **report + block** + filtro + EULA tolerancia cero + moderación ≤24h.
- [ ] **Privacy Nutrition Labels** + Privacy Policy URL.
- [ ] **ATT** (App Tracking Transparency) si hay *tracking*.
- [ ] Permisos con textos `*UsageDescription`.
- [ ] *Age rating* correcto (probable 17+).
- [ ] Screenshots por dispositivo + *App Preview* (opcional).
- [ ] **Demo account** + notas de revisor (cómo iniciar/ver un live).
- [ ] Build firmado vía EAS Submit; sin *crashes* en *review*.
- [ ] Cumplir *minimum iOS* y SDK vigentes.

## 12. Checklist de submission — Google Play

- [ ] Cuenta Play Console + verificación de identidad (D-U-N-S si aplica).
- [ ] Bienes digitales vía **Google Play Billing**.
- [ ] **Account deletion** in-app **y** vía web (requisito de Google).
- [ ] **Data Safety form** completo y veraz.
- [ ] UGC policy: report/block/moderación.
- [ ] **Target API level** vigente; app *bundle* (.aab).
- [ ] *Content rating* (cuestionario IARC).
- [ ] **Closed testing**: ≥12 testers, ≥14 días (cuentas nuevas) antes de producción.
- [ ] Store listing + screenshots + *feature graphic*.
- [ ] *App signing* gestionado por Play.
- [ ] *Privacy policy* URL.

---

## 13. Timeline (Gantt resumido)

```
Semana            1   2   3   4   5   6   7   8   9   10
F0 Discovery     [==]
F1 Beta cerrada  [========================]
WS1 Pagos IAP        [==============]
WS2 Trust&Safety     [==========]
WS3 Privacidad           [======]
F3 Hardening/QA                  [======]
F4 Store Ready                       [====]
F5 Submission                            [========]
F6 Launch                                        [==]
```

---

## 14. KPIs post-lanzamiento y estrategia de rollout

**Rollout faseado (Google):** 5% → 20% → 50% → 100%, vigilando crash-free y reseñas en cada salto.  
**Apple:** *phased release* de 7 días activado.

**KPIs:**
- Crash-free sessions ≥ 99.5%
- D1 / D7 / D30 *retention*
- *Conversion* a primera compra de monedas
- Tiempo medio en live / lives iniciados por DAU
- Rating de tienda ≥ 4.3
- Tickets de moderación resueltos < 24h

**Post-launch:** *war room* 72h, *hotfix* readiness (OTA para JS), revisión semanal de reseñas y *funnels*.

---

## 15. Stack de herramientas

| Área | Herramienta |
|------|-------------|
| Gestión | Jira + Confluence |
| CI/CD móvil | EAS Build + EAS Submit |
| Crash/observabilidad | Sentry / Crashlytics |
| Analytics | (a definir) + ATT-compliant |
| QA E2E | Detox o Maestro |
| Beta | TestFlight + Play Internal/Closed Testing |
| Pagos | StoreKit 2 + Google Play Billing (móvil), Stripe (web) |

---

## 16. Gobernanza y ceremonias

- **Daily standup** (15 min) por pod.
- **Sprint planning / review / retro** cada 2 semanas.
- **Weekly status report** con RAG por workstream a stakeholders.
- **Compliance review** semanal hasta Submission Gate.
- **Go/No-Go meeting** antes de cada envío.
- **Release war room** durante el lanzamiento.

---

*Siguientes pasos sugeridos: (1) aprobar este roadmap y el alcance P0; (2) abrir los epics WS1–WS3 como issues; (3) arrancar beta cerrada (TestFlight + Play Internal) en paralelo al build de IAP.*
