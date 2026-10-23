FROM apache/airflow:2.10.5-python3.11

USER airflow
RUN pip install --no-cache-dir \
    pandas==2.2.3 \
    SQLAlchemy==2.0.36 \
    psycopg2-binary==2.9.10 \
    dbt-core==1.9.1 \
    dbt-postgres==1.9.0
