FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY README.md alembic.ini ./
COPY alembic ./alembic
COPY src ./src
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
ENV PATH="/app/.venv/bin:$PATH" PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd --system --uid 10001 app
COPY --from=build /app /app
USER app
EXPOSE 8000
# Apply pending migrations, then serve the API.
CMD ["sh", "-c", "alembic upgrade head && uvicorn business_service.main:app --host 0.0.0.0 --port ${BUSINESS_PORT:-8000}"]
