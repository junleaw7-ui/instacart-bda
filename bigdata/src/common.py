import os
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    ByteType,
    FloatType,
    IntegerType,
    ShortType,
    StringType,
    StructField,
    StructType,
)

DEFAULT_DATA_DIR = r"C:\Users\USER\Desktop\Big Data\Instacart dataset"

ORDERS_SCHEMA = StructType(
    [
        StructField("order_id", IntegerType()),
        StructField("user_id", IntegerType()),
        StructField("eval_set", StringType()),
        StructField("order_number", ShortType()),
        StructField("order_dow", ByteType()),
        StructField("order_hour_of_day", ByteType()),
        StructField("days_since_prior_order", FloatType()),
    ]
)

ORDER_PRODUCTS_SCHEMA = StructType(
    [
        StructField("order_id", IntegerType()),
        StructField("product_id", IntegerType()),
        StructField("add_to_cart_order", ShortType()),
        StructField("reordered", ByteType()),
    ]
)

PRODUCTS_SCHEMA = StructType(
    [
        StructField("product_id", IntegerType()),
        StructField("product_name", StringType()),
        StructField("aisle_id", ShortType()),
        StructField("department_id", ByteType()),
    ]
)


def data_dir() -> str:
    return os.environ.get("INSTACART_DATA_DIR", DEFAULT_DATA_DIR)


def get_spark(app_name: str, driver_memory: str = "4g") -> SparkSession:
    # SPARK_MASTER lets local dev force local[*]; on EMR, leave it unset so
    # spark-submit's --master yarn (and EMR's cluster defaults) take effect --
    # calling .master() here would silently override that and run single-node.
    builder = SparkSession.builder.appName(app_name)
    master = os.environ.get("SPARK_MASTER")
    if master:
        builder = builder.master(master)
    return (
        builder
        .config("spark.driver.memory", driver_memory)
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def read_csv(spark: SparkSession, data_dir_: str, filename: str, schema: StructType):
    path = str(Path(data_dir_) / filename)
    return spark.read.csv(path, header=True, schema=schema)
