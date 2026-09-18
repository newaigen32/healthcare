# Azure AI Search setup

Version 1 queries an existing Azure AI Search index. Document ingestion is out of scope.

## Required Azure values

- Search endpoint, for example `https://<service>.search.windows.net`
- Index name
- Query API key

Put them in `backend/.env` and set `SEARCH_MODE=azure`.

## Index fields

Map your schema with environment variables:

- `AZURE_SEARCH_ID_FIELD` (default `id`)
- `AZURE_SEARCH_TITLE_FIELD` (default `title`)
- `AZURE_SEARCH_CONTENT_FIELD` (default `content`)
- `AZURE_SEARCH_SOURCE_FIELD` (default `source`)
- `AZURE_SEARCH_CATEGORY_FIELD` (default `category`)

Common alternative names that the mapper also checks for content and source:

- content: `chunk`, `text`
- source: `metadata_storage_name`, `sourcefile`

## Hybrid search

Set `AZURE_SEARCH_VECTOR_FIELD` to the embedding field on the index (for example `contentVector`).

Hybrid search in this project uses `VectorizableTextQuery`. That requires the index field to have an Azure Search **vectorizer** so the service can embed the query text. If you only stored vectors at index time and do not have a vectorizer, leave the vector field empty. Keyword search will continue to work, and hybrid can be enabled later without changing the API.

Optional semantic ranking: set `AZURE_SEARCH_SEMANTIC_CONFIGURATION` to the semantic configuration name defined on the index.
