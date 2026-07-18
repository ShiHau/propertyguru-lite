FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Copy root workspace and frontend structure
COPY pyproject.toml uv.lock ./
COPY frontend/pyproject.toml ./frontend/

# Sync only frontend packages
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev --package frontend

# Runtime container
FROM python:3.13-alpine
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy frontend source code
COPY frontend/ ./frontend/

EXPOSE 8080
CMD ["uvicorn", "frontend.main:app", "--host", "0.0.0.0", "--port", "8080"]
