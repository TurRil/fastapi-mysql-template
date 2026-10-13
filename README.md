# Simple FastAPI App

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open http://127.0.0.1:8000/ for the Jinja2-rendered home page.

The status endpoint at http://127.0.0.1:8000/api/status returns:

```json
{"status": "ok"}
```

Interactive API documentation is available at http://127.0.0.1:8000/docs.

## Run with Docker

```powershell
Copy-Item .env.example .env   # then change the passwords
docker compose up -d --build
```

This runs the app on Python 3.14 at http://127.0.0.1:8000/ and MySQL 9 in a
`db` service. The app connects to `db` over the Compose network; MySQL data is
kept in the `mysql-data` volume. Set `WEB_PORT` or `MYSQL_HOST_PORT` in `.env`
if 8000 or 3306 is already in use on your machine.

To connect with MySQL Workbench, use host `127.0.0.1`, port `MYSQL_HOST_PORT`
(default `3306`), and either `APP_DB_USER`/`APP_DB_PASSWORD` or `root` with
`MYSQL_ROOT_PASSWORD`. The port is bound to localhost only. Credentials are
applied when the volume is first created; after changing them, run
`docker compose down -v` (this deletes the database data) and start again.

## Configuration

`app/settings.py` defines the `Settings` class and a shared `settings` instance.
Configuration is read from environment variables or an optional `.env` file in
the project root. Environment variables take precedence over `.env` values.

```dotenv
APP_TITLE=FastAPI
APP_VERSION=0.1.0
APP_DEBUG=false
APP_API_PREFIX=/api
```

These are the defaults. Restart the application after changing configuration.
Keep debug mode disabled outside local development. The `.env` file is ignored
by Git.

`APP_API_PREFIX` controls where the API router is mounted. It must start with
`/` and must not end with `/`. For example, `/api/v1` exposes the status route at
`/api/v1/status`. The home page's status link follows the configured prefix.

## Database

SQLAlchemy uses PyMySQL to connect to MySQL. Set these values in `.env` or the
environment:

```dotenv
APP_DB_HOST=localhost
APP_DB_PORT=3306
APP_DB_USER=root
APP_DB_PASSWORD=
APP_DB_NAME=simple
```

Use a dedicated database user and a strong password outside local development.
Create the database separately; the application does not create databases or
tables at startup. `Settings.database_url` builds the connection URL safely,
including credentials with special characters, and uses `utf8mb4`.

Define SQLAlchemy models by inheriting from `Base` in `app/db/models.py`.
Use `get_db` from `app/db/session.py` as a FastAPI dependency:

```python
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

DatabaseSession = Annotated[Session, Depends(get_db)]
```

Declare a `db: DatabaseSession` parameter in synchronous (`def`) database route
handlers because PyMySQL performs blocking I/O. Sessions close after each request;
call `db.commit()` explicitly when saving changes. Connections are opened lazily,
when a query first runs. The `/api/status` route remains an application status
check, not a database health check.

FastAPI's lifespan makes the shared engine and session factory available as
`app.state.db_engine` and `app.state.db_session_factory`. The connection pool
is disposed on shutdown. Startup does not open or verify a MySQL connection.

## Structure

- `main.py`: creates the application, manages database lifespan, and registers the routers.
- `app/settings.py`: application configuration using Pydantic settings.
- `app/db/models.py`: shared SQLAlchemy model base and model definitions.
- `app/db/session.py`: database engine, session factory, and session dependency.
- `app/site/routes.py`: UI routes.
- `app/site/templates/home.html`: home page template.
- `app/api/routes.py`: API routes, mounted under `/api`.

The routers live under `app` to avoid colliding with Python's built-in `site` module.