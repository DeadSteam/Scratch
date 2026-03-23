#!/bin/bash
# Creates a read-only PostgreSQL user for experiments_db.
# Runs automatically on first container creation (Docker initdb.d).
# For an already-running container use: sql/create_readonly_user.sql
set -e

RO_PASSWORD="${READONLY_DB_PASSWORD:-changeme}"

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<-EOSQL
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'readonly') THEN
      CREATE ROLE readonly WITH LOGIN PASSWORD '$RO_PASSWORD';
    END IF;
  END
  \$\$;

  GRANT CONNECT ON DATABASE "$POSTGRES_DB" TO readonly;
  GRANT USAGE ON SCHEMA public TO readonly;
  GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
  ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly;
EOSQL

echo "Read-only user 'readonly' created/verified."
