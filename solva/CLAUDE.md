# Solva — Project Rules

## Stack
- Expo SDK 55 + React Native 0.83 + React 19
- expo-router (file-based routing en app/)
- TypeScript strict
- Supabase (auth, DB, Edge Functions, Storage)
- Stripe (EU) — @stripe/stripe-react-native (nativo) / @stripe/react-stripe-js (web)
- i18next (7 idiomas: en, es, fr, pt, nl, de, it)

## Idioma
- Código, variables, tipos, commits y comentarios: en inglés
- Strings de UI: siempre con i18n (t('key')), nunca hardcodeados
- Textos legales (contracts/templates.ts): idioma local del país

## Estructura
- app/          → pantallas (expo-router)
- components/   → componentes reutilizables
- hooks/        → hooks custom
- lib/          → contextos, clientes, tipos, utilidades
- supabase/     → migraciones + Edge Functions (Deno/TypeScript)
- plugins/      → config plugins de Expo

## Reglas de código

### TypeScript
- strict: true — no usar `any` salvo en tipos de Supabase responses
- No duplicar interfaces — un solo lugar para cada tipo (lib/supabase.ts)
- Exportar tipos junto al módulo que los define

### React Native
- Platform-specific: usar extensiones .web.tsx / .tsx (Metro lo resuelve)
- No usar window.*, document.*, navigator.* directamente — siempre Platform.OS check
- StyleSheet.create para estilos, no objetos inline (salvo excepciones simples)
- useEffect: siempre declarar dependencias completas y cleanup si hay suscripciones

### Supabase
- Queries: siempre manejar { data, error } — no ignorar error
- Usar .maybeSingle() en lugar de .single() cuando la fila puede no existir
- Edge Functions: validar env vars al inicio (Deno.env.get sin !)
- Edge Functions: validar Authorization header antes de usarlo
- Webhooks (Stripe, MP): verify_jwt = false en config.toml + verificar firma en código
- Nunca exponer SUPABASE_SERVICE_ROLE_KEY en responses

### Seguridad
- No hardcodear claves en código fuente — usar env vars
- Stripe publishable keys van en eas.json env (por perfil)
- Server secrets van en Supabase secrets (nunca en código)
- CORS: nunca Access-Control-Allow-Origin: * en producción
- Fetch externo: siempre con AbortSignal.timeout()
- Uploads: validar tamaño y content-type

### Commits
- Formato: tipo(scope): descripción
- Tipos: fix, feat, chore, refactor, docs
- Scope: solva, solva/backend, solva/i18n, etc.
- En español o inglés, consistente dentro del commit

### Lo que NO hacer
- No commitear archivos .env, .zip, binarios, ni archivos de 0 bytes
- No usar expo.install.exclude salvo necesidad documentada
- No dejar código muerto (if false, imports no usados, plugins no registrados)
- No crear archivos nuevos si puedes editar uno existente
