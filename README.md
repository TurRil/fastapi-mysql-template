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

The status endpoint at http://127.0.0.1:8000/status returns:

```json
{"status": "ok"}
```

Interactive API documentation is available at http://127.0.0.1:8000/docs.

## API Endpoints

The API is available at the root of the application (there is no `/api` prefix).

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/status` | Returns `{"status":"ok"}`. |
| `POST` | `/transactions` | Categorizes and saves a transaction; returns the saved transaction with HTTP `201`. Requires `OPENAI_API_KEY`. |
| `GET` | `/transactions` | Returns transactions, newest first. |
| `GET` | `/transactions/{transaction_id}` | Returns one transaction, or HTTP `404` if it does not exist. |

Submit a transaction with these fields:

```json
{
	"transaction_id": "TXN00001",
	"amount": -87.18,
	"transaction_date": "2024-05-16T07:22:18.808433",
	"description": "Municipal Tax Payment",
	"transaction_type": "debit",
	"account_number": "NLINGB1944573686"
}
```

The response includes the submitted fields, `created_at`, and the generated
integer `classification`.

The endpoint returns HTTP `503` when the key is missing and
HTTP `502` if categorization fails.

`GET /transactions` accepts optional query parameters. Combine any of these to
filter results:

| Parameter | Description |
| --- | --- |
| `classification` | Match an integer classification ID. |
| `transaction_type` | Match `debit` or `credit`. |
| `account_number` | Match an account number. |
| `start_date` | Include transactions on or after this ISO 8601 date/time. |
| `end_date` | Include transactions on or before this ISO 8601 date/time. |
| `search` | Case-insensitive substring match on the description. |
| `limit` | Maximum results (`1`-`500`; default `100`). |
| `offset` | Number of matching results to skip (default `0`). |

For example, `/transactions?transaction_type=debit&start_date=2024-01-01T00:00:00&limit=25`
returns up to 25 debit transactions from that date onward.

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

These are the defaults. Restart the application after changing configuration.
Keep debug mode disabled outside local development. The `.env` file is ignored
by Git.

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
- `app/api/routes.py`: API routes, mounted at the application root.

The routers live under `app` to avoid colliding with Python's built-in `site` module.
