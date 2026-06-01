# Python 3.12 — has wheels for faiss/torch/ragas (py3.14 does not).
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# libgomp1: required by faiss-cpu / torch at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install deps first (better layer caching). src needed for the editable build target.
COPY pyproject.toml ./
COPY src ./src
RUN pip install --upgrade pip && pip install -e ".[rag]"

EXPOSE 8000

# Default: the FastAPI app (health + future webhook). The Telegram long-poll
# worker runs as a separate command/service once the composition root lands.
CMD ["uvicorn", "vaos.app:app", "--host", "0.0.0.0", "--port", "8000"]
