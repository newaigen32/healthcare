# Architecture

Version 1 is a search application. Employees ask a question, the system retrieves relevant company documents, and the UI displays those documents. There is no LLM answer generation in this version.

## Request flow

```mermaid
flowchart TD
  employee[Employee]
  web[Next.js web application]
  api[FastAPI backend]
  search[Mock catalog or Azure AI Search]
  docs[Documents]

  employee --> web
  web --> api
  api --> search
  search --> docs
  docs --> search
  search --> api
  api --> web
  web --> employee
```

## Component responsibilities

| Component | Responsibility |
| --- | --- |
| Next.js | Question form, loading/empty/error/no-result states, display of `SearchResult` records |
| FastAPI | Validate requests, CORS, logging, search orchestration |
| Search service | Provider selection (`mock` or `azure`) and mapping to the internal result model |
| Azure AI Search | Keyword search when `SEARCH_PROVIDER=azure` |

The browser never calls Azure Search. The Azure API key stays on the backend.

## Internal search model

Frontends depend on this API shape, not on Azure-specific payloads:

- `id`
- `title`
- `content`
- `source`
- `category`
- `score`

## Search providers

- **mock:** static documents in `backend/app/data/documents.json`
- **azure:** keyword `search_text` against the configured Azure AI Search index

Hybrid/vector search is not enabled yet.

## Version 1.1 (not implemented)

The service layer is intentionally thin so retrieval-augmented generation can be added later without changing the frontend contract for sources:

```mermaid
flowchart TD
  employee[Employee question]
  web[Next.js]
  api[FastAPI]
  search[Azure AI Search]
  docs[Top relevant documents]
  llm[LLM]
  answer[Answer plus sources]

  employee --> web
  web --> api
  api --> search
  search --> docs
  docs --> llm
  llm --> answer
  answer --> web
```

Version 1 stops after returning `docs` to the frontend.
