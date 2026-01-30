FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-traditional \
    postgresql-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# uv — ставим зависимости и проект в этом же образе (venv не копируем из builder)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
COPY src ./src
RUN uv sync --frozen --no-dev

COPY . .

RUN dos2unix entrypoint.sh 2>/dev/null || true && chmod +x entrypoint.sh

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
