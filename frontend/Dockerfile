# FASE 1: Construcción (Node.js)
FROM node:20-alpine AS builder
WORKDIR /app

# The following COPY is usually better:
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build # <-- You must have a build step here for Next.js

# FASE 2: Servidor (Node.js)
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production

# Next.js standalone requires three copies:
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/.next/standalone ./

# If you use modules outside of standalone, you'd also need:
# COPY --from=builder /app/node_modules ./node_modules 
# (But standalone is designed to make this unnecessary)

# Comando de inicio del servidor de Next.js
EXPOSE 3000
CMD ["node", "server.js"]