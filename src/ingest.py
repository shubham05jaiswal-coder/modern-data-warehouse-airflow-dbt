"""Validate and load sample CSV files into PostgreSQL raw tables."""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))

CONTRACTS = {
    "customers": {
        "required": {"customer_id", "customer_name", "email", "city", "signup_date"},
        "unique": ["customer_id"],
        "non_negative": [],
    },
    "products": {
        "required": {"product_id", "product_name", "category", "unit_price"},
        "unique": ["product_id"],
        "non_negative": ["unit_price"],
    },
    "orders": {
        "required": {"order_id", "customer_id", "product_id", "order_date", "quantity", "unit_price", "status"},
        "unique": ["order_id"],
        "non_negative": ["quantity", "unit_price"],
    },
}


class DataContractError(ValueError):
    """Raised when a CSV does not meet its declared data contract."""


def validate_frame(name: str, frame: pd.DataFrame) -> pd.DataFrame:
    """Validate a source frame and return a normalized copy."""
    if name not in CONTRACTS:
        raise DataContractError(f"Unknown dataset: {name}")
    result = frame.copy()
    contract = CONTRACTS[name]
    missing = contract["required"] - set(result.columns)
    if missing:
        raise DataContractError(f"{name}: missing required columns: {sorted(missing)}")

    for column in contract["unique"]:
        if result[column].isna().any():
            raise DataContractError(f"{name}: {column} contains null values")
        if result[column].duplicated().any():
            raise DataContractError(f"{name}: {column} contains duplicate values")

    for column in contract["required"]:
        if result[column].isna().any():
            raise DataContractError(f"{name}: {column} contains null values")

    for column in contract["non_negative"]:
        result[column] = pd.to_numeric(result[column], errors="coerce")
        if result[column].isna().any():
            raise DataContractError(f"{name}: {column} contains non-numeric values")
        if (result[column] < 0).any():
            raise DataContractError(f"{name}: {column} cannot be negative")

    date_columns = {"customers": ["signup_date"], "orders": ["order_date"]}.get(name, [])
    for column in date_columns:
        parsed = pd.to_datetime(result[column], errors="coerce")
        if parsed.isna().any():
            raise DataContractError(f"{name}: {column} contains invalid dates")
        result[column] = parsed.dt.date

    return result


def load_csvs(data_dir: Path = DATA_DIR) -> dict[str, int]:
    """Validate CSVs and replace raw tables in a single database transaction."""
    dsn = os.getenv(
        "WAREHOUSE_DSN",
        "postgresql+psycopg2://warehouse:warehouse_local_only@localhost:5432/analytics",
    )
    engine = create_engine(dsn, pool_pre_ping=True)
    loaded: dict[str, int] = {}
    try:
        frames = {
            name: validate_frame(name, pd.read_csv(data_dir / f"{name}.csv"))
            for name in CONTRACTS
        }
        with engine.begin() as connection:
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))
            for name, frame in frames.items():
                frame.to_sql(
                    name,
                    connection,
                    schema="raw",
                    if_exists="replace",
                    index=False,
                    method="multi",
                    chunksize=500,
                )
                loaded[name] = len(frame)
    finally:
        engine.dispose()
    return loaded


if __name__ == "__main__":
    counts = load_csvs()
    print("Loaded source rows:", counts)
