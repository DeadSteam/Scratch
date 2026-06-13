FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-traditional \
    postgresql-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# uv — fastest Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Best practice: copy from cache instead of linking (required for volumes)
ENV UV_LINK_MODE=copy
# Compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1

# Install dependencies first (layer caching)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy source code and install project
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

RUN dos2unix entrypoint.sh 2>/dev/null || true && chmod +x entrypoint.sh

RUN groupadd --system app \
    && useradd --system --gid app --uid 1000 --home-dir /app app \
    && chown -R app:app /app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

USER app

ENTRYPOINT ["./entrypoint.sh"]
# --proxy-headers/--forwarded-allow-ips are added dynamically by entrypoint.sh,
# pinned to nginx's *current* IP on app-network (resolved via Docker DNS at
# startup, since container IPs are reassigned across recreations).
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-graceful-shutdown", "25"]
