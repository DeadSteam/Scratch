#!/bin/bash
set -e

echo "Starting application..."
echo "Note: Database healthchecks are handled by docker-compose 'depends_on' conditions"

# Wait a bit for services to be fully ready
sleep 3

# При монтировании тома (.:/app) в контейнере нет .venv из образа — ставим зависимости в /app
if [ ! -f /app/.venv/bin/python ]; then
  echo "Setting up virtual environment..."
  uv sync --frozen --no-dev
fi

# Run database migrations (if needed)
# echo "Running database migrations..."
# alembic upgrade head

# Запуск: используем python из .venv (при volume mount PATH не содержит образный .venv)
# CMD приходит как "python" "-m" "uvicorn" ... — подменяем на /app/.venv/bin/python
if [ "$1" = "python" ] && [ "$2" = "-m" ]; then
  shift 2
  exec /app/.venv/bin/python -m "$@"
else
  exec "$@"
fi
