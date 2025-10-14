# FASE 1: Dependencias
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# FASE 2: Build
FROM node:20-alpine AS builder
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# (workaround por si algún FS marca noexec en .bin — no suele ser necesario pero ayuda)
RUN chmod -R +x node_modules/.bin || true
RUN npm run build

# FASE 3: Runtime (production)
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
# Si usas "output: standalone" en next.config, copia .next/standalone:
# COPY --from=builder /app/.next/standalone ./
# COPY --from=builder /app/public ./public
# CMD ["node","server.js"]

# Si NO usas standalone:
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node","node_modules/next/dist/bin/next","start","-p","3000"]
