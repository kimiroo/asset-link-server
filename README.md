# Asset Link API Server

### Environment Variables

- **`DATABASE_URL`** (Required)
  - Description: PostgreSQL database connection URI
  - Options: Any valid connection string

- **`REDIS_HOST`** (Required)
  - Description: Hostname or IP address of the Redis server
  - Options: Any valid hostname or IP

- **`REDIS_PORT`** (Required)
  - Description: Port number on which the Redis server is listening
  - Options: Any valid port number

- **`LOG_LEVEL`** (Optional, Default: `INFO`)
  - Description: Application logging verbosity level
  - Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

- **`IS_DEBUG`** (Optional, Default: `false`)
  - Description: Toggles debug mode and extra development features
  - Options: `true`, `false`

### Alembic Database Migrations

Use Alembic to track changes in your database schema and apply them to your production database.

```bash
# 1. Automatically detect model changes and generate a migration script
poetry run alembic revision --autogenerate -m "message"

# 2. Apply all pending migrations to the Supabase database
poetry run alembic upgrade head