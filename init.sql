-- Создаем пользователя, если он не существует
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'admin') THEN
    CREATE ROLE admin WITH LOGIN PASSWORD 'admin_password';
  END IF;
END $$;

-- Предоставляем права на все таблицы в схеме public
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;

-- Предоставляем права на будущие таблицы
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO admin;