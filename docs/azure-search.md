# Azure AI Search setup

This milestone queries an existing Azure AI Search index with **keyword search**. Document ingestion, hybrid/vector search, and LLM/RAG answers are out of scope.

## Required Azure values

- Search endpoint, for example `https://<service>.search.windows.net`
- Index name
- Query API key

Put them in a gitignored `.env` (repository root and/or `backend/.env`) and set:

```
SEARCH_PROVIDER=azure
AZURE_SEARCH_ENDPOINT=https://<service>.search.windows.net
AZURE_SEARCH_INDEX_NAME=<index-name>
AZURE_SEARCH_API_KEY=<query-key>
```

Do not put these values in `docker-compose.yml` or in the frontend container.

## Index fields

The backend maps Azure documents onto the existing API `SearchResult` model.

| API field | Default Azure field | Fallback names |
| --- | --- | --- |
| `id` | `id` | — |
| `title` | `title` | untitled if missing |
| `content` | `content` | `chunk`, `text` |
| `source` | `source` | `metadata_storage_name`, `sourcefile` |
| `category` | `category` | omitted if missing |
| `score` | `@search.score` | omitted if missing |

Override names with `AZURE_SEARCH_*_FIELD` environment variables if your index differs.

## Score

Azure keyword ranking uses BM25-style `@search.score` values. They are **not** guaranteed to be between 0 and 1. The API passes the raw score through. The UI shows it as “Relevance {score}” with two decimal places.

## Hybrid / vector search

Not enabled in this milestone. Keyword `search_text` only.
