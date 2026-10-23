# Modern Data Warehouse: Airflow + dbt + PostgreSQL

An end-to-end, reproducible data engineering portfolio project. It ingests CSV order data into PostgreSQL, transforms it into analytics-ready warehouse models with dbt, and orchestrates the workflow with Apache Airflow.

> Portfolio/demo project using synthetic data. It is not a production deployment. Production use requires secrets management, access controls, monitoring, backup/restore testing, and workload-specific validation.

## Architecture

```mermaid
flowchart LR
    A[CSV source files] --> B[Python ingestion + validation]
    B --> C[(PostgreSQL raw schema)]
    C --> D[dbt staging models]
    D --> E[Dimensions and fact table]
    E --> F[Daily sales mart]
    G[Apache Airflow] --> B
    G --> H[dbt run + dbt test]
    H --> D
    F --> I[BI / SQL consumers]
```

### Stack
- Python 3.11, pandas, SQLAlchemy
- PostgreSQL 16
- Apache Airflow 2.10
- dbt Core + dbt-postgres
- Docker Compose and pytest

## Repository layout

```text
dags/warehouse_pipeline.py
data/{customers,products,orders}.csv
dbt/
  dbt_project.yml
  profiles.yml
  models/sources.yml
  models/staging/{stg_customers,stg_products,stg_orders}.sql
  models/marts/{dim_customers,dim_products,fct_orders,mart_daily_sales}.sql
  models/marts/schema.yml
  tests/positive_order_amounts.sql
src/ingest.py
tests/test_ingest.py
.env.example
.gitignore
Dockerfile
docker-compose.yml
requirements.txt
```

## Quick start (Docker)

Prerequisites: Docker Desktop or Docker Engine with Compose, and at least 4 GB RAM available for the containers.

1. Copy the environment file:

   **PowerShell**
   ```powershell
   Copy-Item .env.example .env
   ```

   **macOS/Linux**
   ```bash
   cp .env.example .env
   ```
2. Start services: `docker compose up --build -d`.
3. Wait for Airflow to initialize, then open <http://localhost:8080>. Airflow Standalone creates an admin user and prints the generated password in the container logs; retrieve it with `docker compose logs airflow`.
4. Enable the `warehouse_pipeline` DAG and trigger it manually.
5. Inspect the daily sales mart:
   ```bash
   docker compose exec warehouse psql -U warehouse -d analytics -c "SELECT * FROM analytics.mart_daily_sales ORDER BY order_date;"
   ```
6. Follow logs with `docker compose logs -f airflow`.

Stop services with `docker compose down`. Delete the local database volume and demo data with `docker compose down -v`.

## Run ingestion and tests without Docker

Requires Python 3.11 and a reachable PostgreSQL database.

```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Set `WAREHOUSE_DSN` to a PostgreSQL SQLAlchemy URL, e.g. `postgresql+psycopg2://warehouse:warehouse_local_only@localhost:5432/analytics`.

```bash
python -m src.ingest
pytest -q
```

The ingestion unit tests use temporary in-memory data and do not require PostgreSQL.

## Data model

- `raw.customers`, `raw.products`, `raw.orders`: source-shaped raw tables.
- `analytics.stg_customers`, `analytics.stg_products`, `analytics.stg_orders`: cleaned dbt staging views.
- `analytics.dim_customers`, `analytics.dim_products`: dimensions.
- `analytics.fct_orders`: order-grain fact table with sales amount.
- `analytics.mart_daily_sales`: daily revenue, completed orders, units, and average order value.

The sample data is synthetic and intentionally small. This starter model assumes `order_id` is unique; sources with multiple lines per order should use a composite key like `(order_id, order_line_id)`.

## Data quality and testing

Python validates required columns, nulls, duplicate IDs, non-negative quantities/prices, and date formats. dbt tests check key uniqueness, non-null keys, and relationships. A singular SQL test flags negative sales amounts. pytest covers CSV validation.

## Portfolio extensions

1. Add incremental models and idempotent merge/upsert semantics.
2. Add dbt snapshots to demonstrate Type 2 history for customer attributes.
3. Add Great Expectations or Soda checks and a quarantine table for rejected rows.
4. Add CI with GitHub Actions for lint, pytest, and dbt parse.
5. Add a Power BI report with revenue, order count, units, average order value, and category trends.
6. Deploy to a managed PostgreSQL service only after setting budgets and spending alerts.

## Security notes

- `.env` is ignored by Git; never commit credentials or production data.
- Demo credentials are local-only.
- Do not expose PostgreSQL or Airflow publicly with demo settings. Use authentication, TLS, network restrictions, and proper secrets management in any deployment.
- This project uses synthetic sample data.

## Suggested topics

`data-engineering` `apache-airflow` `dbt` `postgresql` `python` `etl` `data-warehouse` `docker` `analytics`
