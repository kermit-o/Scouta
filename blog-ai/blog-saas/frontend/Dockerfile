FROM node:20-slim
ARG CACHE_BUST=1773702689

WORKDIR /app

COPY package*.json ./
RUN npm install
RUN rm -rf .next

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
# rebuild Sat Feb 21 21:17:26 UTC 2026
# rebuild Sat Feb 21 21:19:02 UTC 2026
# rebuild Sat Mar 14 02:40:56 UTC 2026
# 1773634366
# 1773634383
# 1773634393
