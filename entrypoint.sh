#!/bin/bash
set -e

echo "=== Scratch App Entrypoint ==="

# Wait a bit for services to be fully ready
sleep 2

# -----------------------------------------------------------------------
# Always sync dependencies.
# When a named volume (app_venv) caches .venv, new packages added to
# pyproject.toml won't be present until we run uv sync.  uv is fast
# enough that a no-op sync takes < 1 second.
# -----------------------------------------------------------------------
echo "Syncing dependencies..."
uv sync --frozen --no-dev 2>&1 || {
  echo "uv sync --frozen failed, trying without --frozen..."
  uv sync --no-dev 2>&1
}
echo "Dependencies OK"

# -----------------------------------------------------------------------
# Run Alembic migrations (only if migration files exist)
# -----------------------------------------------------------------------
for db in main users knowledge; do
  versions_dir="/app/alembic/${db}/versions"
  # Count actual migration .py files (exclude __pycache__, .gitkeep)
  migration_count=$(find "$versions_dir" -maxdepth 1 -name '*.py' 2>/dev/null | wc -l)
  if [ "$migration_count" -gt 0 ]; then
    echo "Running migrations for ${db} DB (${migration_count} files)..."
    /app/.venv/bin/python -m alembic -x db=${db} upgrade head || {
      echo "WARNING: ${db} DB migration failed (non-fatal)"
    }
  else
    echo "No migrations for ${db} DB — skipping"
  fi
done

# -----------------------------------------------------------------------
# Execute CMD / command override
# -----------------------------------------------------------------------
if [ "$1" = "python" ] && [ "$2" = "-m" ]; then
  shift 2
  exec /app/.venv/bin/python -m "$@"
else
  exec "$@"
fi
