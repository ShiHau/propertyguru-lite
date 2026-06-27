# PropertyGuru Lite

FastAPI backend for a real-estate leads management system.

Current status:
- Core business rules implemented (duplicate checks, assignment strategy pipeline)
- Agent/admin user split implemented at data model level
- Authentication not implemented yet (temporary `user_id` query parameter is used in agent routes)

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
ASSIGNMENT_STRATEGY=round_robin_load_aware
```

## 3) Reset and Seed Database (Recommended for Dev)

The seed script now resets schema and loads mock data in one run.

```bash
python data/load_mock_data.py
```

What this does:
- Drops all tables
- Recreates all tables from current models
- Loads mock admins, agents, listings, and leads from CSV files in `data/`

Important:
- Stop the API server before running this script (SQLite file lock).

## 4) Run API Server

```bash
uvicorn backend.main:app --reload
```

Server:
- API root: http://localhost:8000/
- Swagger docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Development

1. Pull latest changes
2. `uv sync`
3. `python data/load_mock_data.py`
4. `uvicorn backend.main:app --reload`
5. Test endpoints from `/docs` or curl

## Temporary Auth Note

Authentication/authorization dependencies are not wired yet.
Until JWT auth is added:
- Agent identity is passed as `user_id` query parameter on agent routes.
- Admin update/delete user routes require `role` query parameter to disambiguate overlapping IDs between `agents` and `admins`.

## Mock Data Files

- `data/admins.csv`
- `data/agents.csv`
- `data/listings.csv`
- `data/leads.csv`
- `data/users.csv` (legacy, unused by current loader)

Notes:
- Leads reference listings by `listing_id` (not listing title).
- Leads `assigned_agent_id` should point to seeded agent IDs.

## Project Layout

```text
backend/
  api/            # API package
    api/          # Route modules (admins.py, agents.py, auth.py, clients.py)
    schema/       # Shared Pydantic schemas
  db/             # Engine, session factory, Base
  lib/            # Domain and shared application logic
  models/         # ORM re-exports
  config.py       # Settings from .env
  main.py         # FastAPI app startup

data/
  admins.csv
  agents.csv
  load_mock_data.py
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

### Agent routes return "Agent not found"

Likely causes:
- `user_id` query parameter is missing
- `user_id` does not exist in `agents` table

Use a valid seeded agent ID (after running `python data/load_mock_data.py`).

### User update/delete for admin fails to target expected record

When using:
- `PATCH /api/v1/admin/users/{user_id}`
- `DELETE /api/v1/admin/users/{user_id}`

You must pass `role=agent` or `role=admin` in query params.
