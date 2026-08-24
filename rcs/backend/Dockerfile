# syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

# libpq is required by asyncpg (PostgreSQL driver)
RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY rcs/backend/pyproject.toml ./
RUN pip install --no-cache-dir flit && flit install --deps production

COPY rcs/backend/ ./
COPY shared/python/ /app/_shared/
ENV PYTHONPATH=/app:/app/_shared

EXPOSE 8100
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import httpx; httpx.get('http://localhost:8100/health').raise_for_status()"
CMD ["uvicorn", "rcs.main:app", "--host", "0.0.0.0", "--port", "8100"]
