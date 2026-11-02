FROM node:22.16.0-alpine
WORKDIR /app
COPY aula-nova/ .
EXPOSE 3000
CMD ["node", "backend/server.js"]
