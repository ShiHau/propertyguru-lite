FROM ghcr.io/astral-sh/uv:python3.13-alpine AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Copy root workspace and backend structure
COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml ./backend/

# Sync only backend packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package backend

# Runtime container
FROM python:3.13-alpine
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy code paths
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Expose port and run
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
