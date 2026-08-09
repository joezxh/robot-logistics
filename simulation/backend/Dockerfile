# syntax=docker/dockerfile:1
#
# Build context is the repository root so the sibling `rcs/` and `shared/`
# subprojects are reachable when running in embedded mode:
#   docker build -f simulation/backend/Dockerfile -t robot-logic-api .
#
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

COPY simulation/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Simulation backend package (importable as `backend.*`).
COPY simulation/backend ./backend
# RCS subproject — needed only when RCS_EMBEDDED=1 (the default).
COPY rcs/rcs ./rcs
COPY rcs/requirements.txt /tmp/rcs-requirements.txt
RUN pip install --no-cache-dir -r /tmp/rcs-requirements.txt && rm /tmp/rcs-requirements.txt
# Shared MQTT contracts.
COPY shared/python ./_shared

ENV PYTHONPATH=/app:/app/_shared

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
