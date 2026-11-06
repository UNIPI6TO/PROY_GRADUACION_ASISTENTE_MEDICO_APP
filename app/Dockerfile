FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# 1. Dependencias (se cachean mientras requirements.txt no cambie)
COPY requirements.txt .
# torch solo-CPU primero: la imagen baja de ~6 GB a menos de 2 GB
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Modelo de embeddings DENTRO de la imagen: no se descarga en cada arranque
ENV HF_HOME=/app/.cache/huggingface
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')"

# 2. Código y datos de solo lectura
COPY . .
# Índice del RAG construido durante el build (solo si su ingest no necesita claves)
# RUN python scripts/ingest.py

# 3. Usuario sin privilegios
RUN useradd --create-home app && chown -R app /app
USER app

# 4. Arranque: la plataforma indica el puerto en PORT
ENV PORT=8080
EXPOSE 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]