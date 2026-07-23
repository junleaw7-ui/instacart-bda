import os
from pathlib import Path

import pandas as pd

DEFAULT_DATA_DIR = r"C:\Users\USER\Desktop\Big Data\Instacart dataset"


def data_dir() -> Path:
    return Path(os.environ.get("INSTACART_DATA_DIR", DEFAULT_DATA_DIR))


def load_orders(data_dir_: Path) -> pd.DataFrame:
    return pd.read_csv(
        data_dir_ / "orders.csv",
        dtype={
            "order_id": "int32",
            "user_id": "int32",
            "eval_set": "category",
            "order_number": "int16",
            "order_dow": "int8",
            "order_hour_of_day": "int8",
            "days_since_prior_order": "float32",
        },
    )


def load_products(data_dir_: Path) -> pd.DataFrame:
    return pd.read_csv(
        data_dir_ / "products.csv",
        dtype={"product_id": "int32", "aisle_id": "int16", "department_id": "int8"},
    )


def iter_order_products_prior_chunks(data_dir_: Path, chunksize: int = 5_000_000, nrows: int | None = None):
    return pd.read_csv(
        data_dir_ / "order_products__prior.csv",
        dtype={
            "order_id": "int32",
            "product_id": "int32",
            "add_to_cart_order": "int16",
            "reordered": "int8",
        },
        chunksize=chunksize,
        nrows=nrows,
    )
