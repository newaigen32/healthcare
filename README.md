# Knowledge Assistant

Version 1 of an enterprise AI Knowledge Assistant. Employees ask a question in a web app. The Next.js UI calls a FastAPI backend. This milestone returns a **static document catalog** from `backend/app/data/documents.json` so every successful search shows the same source cards. Azure AI Search is the next milestone and is not used yet.

This version does **not** generate LLM answers.

## Architecture

```
Employee
  → Next.js web application
    → FastAPI backend
      → Static document catalog
        → Frontend search results
```

See [docs/architecture.md](docs/architecture.md) for a diagram and extension notes for Version 1.1 (RAG).

## Technology stack

- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** Python, FastAPI, Pydantic, Azure AI Search SDK
- **Search:** Azure AI Search (keyword first; hybrid when a vector field is configured)

## Repository structure

```
frontend/          Next.js application
backend/           FastAPI application
docs/              Architecture and Azure Search setup
docker-compose.yml Run frontend and backend together
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
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)

The browser calls FastAPI at `http://localhost:8000`. That URL is baked into the frontend image at build time (`NEXT_PUBLIC_API_URL`). Do not point it at the Docker service name `backend`; the browser cannot resolve that.

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

The default backend `SEARCH_MODE` is `mock`, so you can run the full UI without Azure credentials.

## Environment variables

### Frontend (`frontend/.env.local`)

| Variable | Purpose |
| --- | --- |
| `NEXT_PUBLIC_API_URL` | FastAPI base URL. Local default: `http://localhost:8000` |

The browser never receives the Azure Search API key. It only calls FastAPI.

### Backend (`backend/.env`)

| Variable | Required | Purpose |
| --- | --- | --- |
| `SEARCH_MODE` | yes | `mock` or `azure` |
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
| `AZURE_SEARCH_VECTOR_FIELD` | no | Vector field name. Empty = keyword search only |
| `AZURE_SEARCH_VECTOR_K` | no | `k` for vector nearest neighbors |
| `AZURE_SEARCH_SEMANTIC_CONFIGURATION` | no | Semantic ranker configuration name |

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
4. `SearchService` reads static documents from `backend/app/data/documents.json` via `StaticSearchProvider`.
5. The same catalog is returned for any non-empty query, with `total` set to the number of documents.
6. Results use the stable `SearchResult` model (`id`, `title`, `content`, `source`, `category`, `score`).

Azure AI Search is not used yet. Later, `StaticSearchProvider` can be replaced with an Azure provider without changing the frontend.

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
- **`SEARCH_MODE=azure` fails at startup.** Set `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_INDEX_NAME`, and `AZURE_SEARCH_API_KEY`.
- **Empty or poorly mapped results.** Your index field names may differ. Update the `AZURE_SEARCH_*_FIELD` variables.
- **Hybrid search errors.** The vector field name may be wrong, or the index may not have a text vectorizer. Clear `AZURE_SEARCH_VECTOR_FIELD` to fall back to keyword search.
- **401/403 from Azure.** The API key is invalid or does not have query permission. The UI only shows a friendly error; details stay in backend logs (without secrets).
- **Timeouts.** Increase `AZURE_SEARCH_TIMEOUT_SECONDS` or check network access to the search endpoint.
