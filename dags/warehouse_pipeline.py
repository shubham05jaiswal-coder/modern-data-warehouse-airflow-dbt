from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT = "/opt/airflow/project"
DBT = f"cd {PROJECT}/dbt && dbt"

with DAG(
    dag_id="warehouse_pipeline",
    description="Load CSVs into PostgreSQL, build dbt models, and run data tests",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["portfolio", "postgres", "dbt"],
) as dag:
    ingest = BashOperator(
        task_id="ingest_csv_to_raw",
        bash_command=f"python {PROJECT}/src/ingest.py",
        env={"WAREHOUSE_DSN": "postgresql+psycopg2://warehouse:warehouse_local_only@warehouse:5432/analytics"},
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"{DBT} run --profiles-dir {PROJECT}/dbt",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"{DBT} test --profiles-dir {PROJECT}/dbt",
    )

    ingest >> dbt_run >> dbt_test
