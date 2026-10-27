# frontend/Dockerfile - Servicio Frontend: guiavital (Cloud Run)
# Contexto de compilación esperado: ./frontend (docker build -f frontend/Dockerfile ./frontend)
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Vite incrusta las variables con prefijo VITE_ en tiempo de compilación.
# Por defecto usa '/backend' para enrutar a través del proxy autenticado con OIDC en Nginx.
ARG VITE_API_URL=/backend
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Etapa de ejecución ligera y sin privilegios root
FROM nginxinc/nginx-unprivileged:1.27-alpine AS runner

ENV PORT=8080 \
    BACKEND_URL=http://localhost:8000

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Script de arranque que obtiene y renueva el token OIDC de guiavital-frontend-sa
# desde el Metadata Server de Cloud Run para invocar de forma privada a guiavital-backend
USER root
RUN cat << 'EOF' > /usr/local/bin/start-nginx.sh && chmod +x /usr/local/bin/start-nginx.sh
#!/bin/sh
set -e

refresh_oidc_token() {
  TOKEN=$(wget -q -O - --header="Metadata-Flavor: Google" \
    "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=${BACKEND_URL}" 2>/dev/null || true)
  if [ -n "$TOKEN" ]; then
    printf 'proxy_set_header Authorization "Bearer %s";\n' "$TOKEN" > /tmp/oidc_auth.conf
  else
    : > /tmp/oidc_auth.conf
  fi
}

refresh_oidc_token
envsubst '${PORT} ${BACKEND_URL}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Renovar token OIDC cada 30 minutos en segundo plano (los tokens duran 60 min)
(
  while true; do
    sleep 1800
    refresh_oidc_token
    nginx -s reload >/dev/null 2>&1 || true
  done
) &

exec nginx -g "daemon off;"
EOF

USER 101

EXPOSE 8080

CMD ["/usr/local/bin/start-nginx.sh"]
