import pandas as pd
import pytest

from src.ingest import DataContractError, validate_frame


def customer_frame():
    return pd.DataFrame(
        [{
            "customer_id": 1,
            "customer_name": "Asha Rao",
            "email": "asha@example.test",
            "city": "Pune",
            "signup_date": "2025-01-01",
        }]
    )


def test_valid_customers_are_accepted():
    result = validate_frame("customers", customer_frame())
    assert len(result) == 1
    assert str(result.loc[0, "signup_date"]) == "2025-01-01"


def test_missing_required_column_is_rejected():
    frame = customer_frame().drop(columns=["email"])
    with pytest.raises(DataContractError, match="missing required columns"):
        validate_frame("customers", frame)


def test_duplicate_customer_id_is_rejected():
    frame = pd.concat([customer_frame(), customer_frame()], ignore_index=True)
    with pytest.raises(DataContractError, match="duplicate"):
        validate_frame("customers", frame)


def test_negative_product_price_is_rejected():
    frame = pd.DataFrame([{
        "product_id": 1,
        "product_name": "Keyboard",
        "category": "Accessories",
        "unit_price": -1.0,
    }])
    with pytest.raises(DataContractError, match="cannot be negative"):
        validate_frame("products", frame)


def test_invalid_order_date_is_rejected():
    frame = pd.DataFrame([{
        "order_id": 1,
        "customer_id": 1,
        "product_id": 1,
        "order_date": "not-a-date",
        "quantity": 1,
        "unit_price": 20.0,
        "status": "completed",
    }])
    with pytest.raises(DataContractError, match="invalid dates"):
        validate_frame("orders", frame)
