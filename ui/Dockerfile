FROM node:20-alpine

WORKDIR /app

RUN npm install --global npm@latest

COPY package.json tsconfig.json vite.config.ts index.html ./
COPY src ./src

RUN npm install --legacy-peer-deps

EXPOSE 3300

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3300"]
