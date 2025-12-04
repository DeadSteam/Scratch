#!/bin/bash
set -e

echo "Starting application..."
echo "Note: Database healthchecks are handled by docker-compose 'depends_on' conditions"

# Wait a bit for services to be fully ready
sleep 3

# Run database migrations (if needed)
# echo "Running database migrations..."
# alembic upgrade head

# Start the application
exec "$@"
