# app/Dockerfile - Servicio Backend: guiavital-backend (Cloud Run)
# Contexto de compilación esperado: raíz del repositorio (docker build -f app/Dockerfile .)
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /workspace

# Crear usuario sin privilegios (Principio de mínimo privilegio SRE)
RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --shell /sbin/nologin --no-create-home appuser

# Instalar dependencias definidas en requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente del backend
COPY app/ ./app/

# Asegurar permisos de lectura/ejecución para el usuario no-root
RUN chown -R appuser:appgroup /workspace

USER appuser

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
