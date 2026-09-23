# Database scripts

PostgreSQL schema and sample data live here, not in the FastAPI application.

```
database/
├── scripts/
│   ├── 01_create_tables.sql
│   ├── 02_insert_sample_data.sql
│   ├── 03_verify_data.sql
│   └── 04_cleanup_sample_data.sql
├── migrations/
└── README.md
```

PostgreSQL is the local **source of application data**. Azure AI Search remains a separate provider for later indexing/search.

## Automatic init (first volume only)

Docker Compose mounts `01_create_tables.sql` and `02_insert_sample_data.sql` into `/docker-entrypoint-initdb.d`.

Postgres runs those files **only when the `postgres_data` volume is empty** (first start). Later edits to the SQL files will not rerun until you reset the volume.

`03_verify_data.sql` and `04_cleanup_sample_data.sql` are **manual**. Cleanup is not mounted into initdb.d, because it would delete sample rows on first boot.

## Start the stack

```bash
docker compose up --build
```

## Check containers

```bash
docker compose ps
```

## PostgreSQL health

```bash
docker compose exec db pg_isready -U healthcare_user -d healthcare
```

## Connect

```bash
docker compose exec db psql -U healthcare_user -d healthcare
```

List tables:

```text
\dt
```

View sample records:

```sql
SELECT id, title, document_type FROM documents;
```

## Manual scripts (Windows PowerShell)

Insert sample data (safe to repeat; uses `ON CONFLICT DO NOTHING`):

```powershell
Get-Content .\database\scripts\02_insert_sample_data.sql |
docker compose exec -T db psql -U healthcare_user -d healthcare
```

Verify:

```powershell
Get-Content .\database\scripts\03_verify_data.sql |
docker compose exec -T db psql -U healthcare_user -d healthcare
```

Cleanup sample rows only (does not drop the database):

```powershell
Get-Content .\database\scripts\04_cleanup_sample_data.sql |
docker compose exec -T db psql -U healthcare_user -d healthcare
```

WSL/macOS/Linux equivalent:

```bash
docker compose exec -T db psql -U healthcare_user -d healthcare < database/scripts/03_verify_data.sql
```

## Reset the local database (destructive)

```bash
docker compose down -v
docker compose up --build
```

`docker compose down -v` **deletes the `postgres_data` volume** and all PostgreSQL data. Do not run it unless you intend to wipe local data.

FastAPI does not create tables or insert sample rows. It only connects with `DATABASE_URL` and queries `documents`.
