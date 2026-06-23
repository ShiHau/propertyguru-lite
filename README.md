# PropertyGuru Lite

FastAPI backend for a real-estate leads system.

## Prerequisites

- Python 3.13+
- uv package manager

Install uv if needed:
- https://github.com/astral-sh/uv

## 1) Install Dependencies

From project root:

```bash
uv sync
```

## 2) Configure Environment

Create a `.env` file in project root.

Minimal local setup:

```env
DATABASE_URL=sqlite:///./propertyguru.db
APP_NAME=PropertyGuru Lite
APP_ENVIRONMENT=development
```

## 3) Reset and Seed Database (Recommended for Dev)

The seed script now resets schema and loads mock data in one run.

```bash
python data/load_mock_data.py
```

What this does:
- Drops all tables
- Recreates all tables from current models
- Loads mock users, listings, and leads from CSV files in `data/`

Important:
- Stop the API server before running this script (SQLite file lock).

## 4) Run API Server

```bash
uvicorn app.main:app --reload
```

Server:
- API root: http://localhost:8000/
- Swagger docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Development

1. Pull latest changes
2. `uv sync`
3. `python data/load_mock_data.py`
4. `uvicorn app.main:app --reload`
5. Test endpoints from `/docs` or curl

## Current API Prefixes

- Client: `/api/v1/client/*`
- Agent: `/api/v1/agent/*`
- Admin: `/api/v1/admin/*`

Examples:
- `GET /api/v1/client/listings?limit=50&skip=0`
- `POST /api/v1/client/inquiries`
- `GET /api/v1/admin/listings?limit=50&skip=0`

## Mock Data Files

- `data/users.csv`
- `data/listings.csv`
- `data/leads.csv`

Notes:
- Leads reference listings by `listing_id` (not listing title).
- Bathrooms are integers in model/schema/CSV.

## Project Layout

```text
app/
  api/            # Route handlers
  models/         # SQLAlchemy ORM models
  schemas/        # Pydantic request/response schemas
  config.py       # Settings from .env
  database.py     # Engine, session factory, Base
  main.py         # FastAPI app startup

data/
  load_mock_data.py
  users.csv
  listings.csv
  leads.csv
```

## Common Commands

```bash
# add dependency
uv add <package>

# add dev-only dependency
uv add --group dev <package>

# lint
ruff check .

# format
ruff format .
```

## Troubleshooting

### DB file lock when resetting data

Symptom:
- "process cannot access ... propertyguru.db"

Fix:
- Stop `uvicorn` first, then run `python data/load_mock_data.py`.

### Only first 10 rows returned

Some endpoints default to `limit=10`.
Use query params, for example:

```text
/api/v1/admin/listings?limit=50&skip=0
```
