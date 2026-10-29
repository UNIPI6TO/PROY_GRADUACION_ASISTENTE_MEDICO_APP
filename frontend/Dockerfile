# frontend/Dockerfile - Servicio Frontend: guiavital (Cloud Run)
# Contexto de compilación esperado: ./frontend (docker build -f frontend/Dockerfile ./frontend)
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite incrusta las variables con prefijo VITE_ en tiempo de compilación
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Etapa de ejecución ligera y sin privilegios root
FROM nginxinc/nginx-unprivileged:1.27-alpine AS runner

ENV PORT=8080

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

USER 101

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
