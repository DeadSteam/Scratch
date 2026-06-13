#!/bin/bash
set -e

echo "=== Scratch App Entrypoint ==="

# uv cache must be writable (bind-mount /app is often root-owned on the host)
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"
mkdir -p "$UV_CACHE_DIR"

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
    /app/.venv/bin/python -m alembic -c "alembic.${db}.ini" -x db=${db} upgrade head || {
      echo "ERROR: ${db} DB migration failed" >&2
      exit 1
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
  if [ "$1" = "uvicorn" ]; then
    # Trust X-Forwarded-For from nginx only, so request.client reflects the
    # real client IP (used for per-IP rate limiting) instead of nginx's own
    # address. nginx's IP on app-network is reassigned across container
    # recreations, so resolve it fresh via Docker's embedded DNS rather than
    # hardcoding it: "*" or a CIDR wide enough to also cover the docker
    # gateway address would let a client forge X-Forwarded-For and pick its
    # own rate-limit bucket. Pinning to nginx's exact current IP makes
    # uvicorn trust only that one hop. If nginx can't be resolved (e.g.
    # standalone run, tests), fall back to no proxy-header trust — the safe
    # pre-existing behaviour (bucket keyed on the direct peer's IP, which
    # clients cannot spoof via X-Forwarded-For).
    NGINX_IP=""
    for _ in 1 2 3 4 5 6 7 8 9 10; do
      NGINX_IP=$(/app/.venv/bin/python -c "import socket; print(socket.gethostbyname('nginx'))" 2>/dev/null) && break
      sleep 1
    done
    if [ -n "$NGINX_IP" ]; then
      echo "Trusting X-Forwarded-For from nginx ($NGINX_IP)"
      exec /app/.venv/bin/python -m "$@" --proxy-headers --forwarded-allow-ips="$NGINX_IP"
    else
      echo "nginx not resolvable; X-Forwarded-For will not be trusted"
      exec /app/.venv/bin/python -m "$@"
    fi
  else
    exec /app/.venv/bin/python -m "$@"
  fi
else
  exec "$@"
fi
