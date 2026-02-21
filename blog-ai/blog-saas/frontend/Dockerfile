FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
# rebuild Sat Feb 21 21:17:26 UTC 2026
# rebuild Sat Feb 21 21:19:02 UTC 2026
