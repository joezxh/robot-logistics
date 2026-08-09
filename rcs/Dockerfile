# syntax=docker/dockerfile:1
#
# Build context is the repository root so the sibling `shared/` subproject is
# reachable:
#   docker build -f rcs/Dockerfile -t robot-logic-rcs .
#
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

COPY rcs/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# RCS package.
COPY rcs/rcs ./rcs
# Shared MQTT contracts (topics + payload models), shared with robot-app.
COPY shared/python ./_shared

ENV PYTHONPATH=/app:/app/_shared

EXPOSE 8100
CMD ["uvicorn", "rcs.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8100"]
