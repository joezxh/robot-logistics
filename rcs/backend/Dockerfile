# syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

COPY rcs/backend/pyproject.toml ./
RUN pip install --no-cache-dir flit && flit install --deps production

COPY rcs/backend/ ./

# RCS 子项目（嵌入式模式需要）
COPY rcs/rcs/ /app/_rcs/
COPY shared/python/ /app/_shared/
ENV PYTHONPATH=/app:/app/_rcs:/app/_shared

EXPOSE 8100
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import httpx; httpx.get('http://localhost:8100/health').raise_for_status()"
CMD ["uvicorn", "rcs_backend.main:app", "--host", "0.0.0.0", "--port", "8100"]
