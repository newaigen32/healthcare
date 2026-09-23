# Knowledge Assistant

Version 1 of an enterprise AI Knowledge Assistant. Employees ask a question in a web app. The Next.js UI calls a FastAPI backend. FastAPI searches **PostgreSQL** by default in Docker (`SEARCH_PROVIDER=postgres`). A static mock catalog and Azure AI Search remain available.

This version does **not** generate LLM answers.

## Architecture

```
Employee
  → Next.js web application
    → FastAPI backend
      → PostgreSQL (local documents)
      → or mock catalog
      → or Azure AI Search (future / optional)
        → Frontend search results
```

See [docs/architecture.md](docs/architecture.md) for a diagram and extension notes for Version 1.1 (RAG).

## Technology stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** Python, FastAPI, Pydantic, Azure AI Search SDK
- **Search:** PostgreSQL (recommended local), mock/static catalog, or Azure AI Search keyword search
- **Database:** PostgreSQL 17 (Docker Compose)

## Repository structure

```
frontend/          Next.js application
backend/           FastAPI application
database/          PostgreSQL SQL scripts (schema, sample data)
docs/              Architecture and Azure Search setup
docker-compose.yml Frontend, FastAPI, and PostgreSQL
README.md
```

## Run with Docker

You need Docker Desktop (or Docker Engine plus Compose).

From the repository root:

```bash
docker compose up --build
```

Then open:

- App: [http://localhost:3000](http://localhost:3000)
- API health: [http://localhost:8000/health](http://localhost:8000/health)
- Search health: [http://localhost:8000/health/search](http://localhost:8000/health/search)
- Database health: [http://localhost:8000/health/database](http://localhost:8000/health/database)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

The browser calls FastAPI at `http://localhost:8000`. That URL is baked into the frontend image at build time (`NEXT_PUBLIC_API_URL`). Do not point it at the Docker service name `backend`; the browser cannot resolve that.

**PostgreSQL mode (recommended local default):**

```bash
cp .env.example .env
# SEARCH_PROVIDER=postgres
docker compose up --build
```

Confirm the database container:

```bash
docker compose ps
docker compose exec db pg_isready -U healthcare_user -d healthcare
```

**Mock mode** (no database required for search; static JSON catalog):

```bash
# in .env
SEARCH_PROVIDER=mock
docker compose up --build
```

**Azure mode:** put credentials in the gitignored root `.env` (never in `docker-compose.yml` or the frontend service):

```
SEARCH_PROVIDER=azure
AZURE_SEARCH_ENDPOINT=https://<service>.search.windows.net
AZURE_SEARCH_INDEX_NAME=<index-name>
AZURE_SEARCH_API_KEY=<query-key>
```

Then:

```bash
docker compose up --build
```

Azure variables are passed only to the backend container. Rebuild is not required when only backend env values change; recreate the backend container:

```bash
docker compose up -d --force-recreate backend
```

Stop the stack with `Ctrl+C`, or:

```bash
docker compose down
```

## Local setup (without Docker)

You need Node.js 20+ and Python 3.11+.

Copy environment files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
```

The default backend `SEARCH_PROVIDER` in sample files is `postgres` for Docker. Unit tests still default to `mock` unless `DATABASE_URL` is set.

## Environment variables

### Frontend (`frontend/.env.local`)

| Variable | Purpose |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | FastAPI base URL. Local default: `http://localhost:8000` |

The browser never receives the Azure Search API key. It only calls FastAPI.

### Backend (`backend/.env`)

| Variable | Required | Purpose |
| --- | --- | --- |
| `SEARCH_PROVIDER` | yes | `postgres`, `mock`, or `azure` |
| `DATABASE_URL` | when `postgres` | SQLAlchemy URL. In Docker: `postgresql+psycopg://healthcare_user:<password>@db:5432/healthcare` |
| `POSTGRES_DB` | Docker | Database name. Default: `healthcare` |
| `POSTGRES_USER` | Docker | Database user. Default: `healthcare_user` |
| `POSTGRES_PASSWORD` | Docker | Password for the Compose PostgreSQL service |
| `CORS_ORIGINS` | yes | Comma-separated allowed origins. Local: `http://localhost:3000` |
| `AZURE_SEARCH_ENDPOINT` | when `azure` | Search service endpoint |
| `AZURE_SEARCH_INDEX_NAME` | when `azure` | Index name |
| `AZURE_SEARCH_API_KEY` | when `azure` | Query key (never send this to the frontend) |
| `AZURE_SEARCH_TIMEOUT_SECONDS` | no | Request timeout |
| `AZURE_SEARCH_TOP` | no | Number of results (default 5) |
| `AZURE_SEARCH_ID_FIELD` | no | Index field mapped to `id` |
| `AZURE_SEARCH_TITLE_FIELD` | no | Index field mapped to `title` |
| `AZURE_SEARCH_CONTENT_FIELD` | no | Index field mapped to `content` |
| `AZURE_SEARCH_SOURCE_FIELD` | no | Index field mapped to `source` |
| `AZURE_SEARCH_CATEGORY_FIELD` | no | Index field mapped to `category` |

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: [http://localhost:8000/health](http://localhost:8000/health)

Search:

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the procedure for handling a denied claim?"}'
```

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## How search works in this milestone

1. The employee submits a question in the Next.js app.
2. `frontend/lib/api.ts` posts `{ "query": "..." }` to FastAPI `POST /api/search`.
3. The API route calls `SearchService`.
4. `SearchService` selects `PostgresSearchProvider`, `MockSearchProvider`, or `AzureSearchProvider` from `SEARCH_PROVIDER`.
5. Postgres mode runs a parameterized `ILIKE` query on `documents` (`id`, title, summary, content). Schema and sample rows come from `database/scripts/`, not from Python. Mock mode reads `backend/app/data/documents.json`. Azure mode runs keyword search against the configured index.
6. Results are mapped into the stable `SearchResult` model (`id`, `title`, `content`, `source`, `category`, `score`) before they leave the backend.

`GET /api/documents/{document_id}` returns one PostgreSQL document for the upcoming details page.

PostgreSQL is the **application/source data** store. Azure AI Search is reserved as a later **indexing/search** layer. FastAPI never creates tables or inserts sample data; see [database/README.md](database/README.md).

### PostgreSQL volume behavior

Files mounted to `/docker-entrypoint-initdb.d` (`01_create_tables.sql` and `02_insert_sample_data.sql`) run **only** when PostgreSQL initializes a **new** data directory.

If the `postgres_data` volume already exists, editing those SQL files will not rerun them automatically.

To reset the local database during development:

```bash
docker compose down -v
docker compose up --build
```

`docker compose down -v` **deletes the local PostgreSQL Docker volume** and therefore deletes the database data. Do not run it unless you intend to wipe local data.

See [docs/azure-search.md](docs/azure-search.md) for field mapping and score notes. Hybrid/vector search is not enabled yet.

## Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

```bash
cd frontend
npm test
```

## Troubleshooting

- **Frontend cannot reach the API.** Confirm FastAPI is running on port 8000 and `NEXT_PUBLIC_API_URL` matches. CORS must include `http://localhost:3000`. With Docker, use `docker compose up --build` and keep both published ports (`3000` and `8000`).
- **`SEARCH_PROVIDER=postgres` fails at startup.** Set `DATABASE_URL`. Inside Compose the hostname must be `db`, not `localhost`.
- **PostgreSQL is not ready.** Wait for `docker compose exec db pg_isready -U healthcare_user -d healthcare`. The backend retries the connection on startup.
- **`SEARCH_PROVIDER=azure` fails at startup.** Set `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX_NAME`, and `AZURE_SEARCH_API_KEY`.
- **Relevance looks larger than 1.** Azure keyword scores are BM25-style and are passed through unchanged.
- **401/403 from Azure.** The API key is invalid or does not have query permission. The UI only shows a friendly error; details stay in backend logs (without secrets).
- **Timeouts.** Increase `AZURE_SEARCH_TIMEOUT_SECONDS` or check network access to the search endpoint.
