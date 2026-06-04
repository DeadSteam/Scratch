 
\set ro_password 'Akrawerkatya'

DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'readonly') THEN
    EXECUTE format('CREATE ROLE readonly WITH LOGIN PASSWORD %L', :'ro_password');
    RAISE NOTICE 'User readonly created.';
  ELSE
    RAISE NOTICE 'User readonly already exists, updating password.';
    EXECUTE format('ALTER ROLE readonly WITH PASSWORD %L', :'ro_password');
  END IF;
END
$$;

-- Доступ к базе
GRANT CONNECT ON DATABASE experiments_db TO readonly;

-- Доступ к схеме
GRANT USAGE ON SCHEMA public TO readonly;

-- SELECT на все существующие таблицы
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

-- SELECT на таблицы, которые будут созданы в будущем
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO readonly;

-- Проверка выданных прав
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'readonly'
ORDER BY table_name;
