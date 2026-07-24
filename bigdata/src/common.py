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
    if data_dir_.startswith("s3://") or data_dir_.startswith("s3a://"):
        path = f"{data_dir_.rstrip('/')}/{filename}"
    else:
        path = str(Path(data_dir_) / filename)
    return spark.read.csv(path, header=True, schema=schema)


def save_csv(pdf, output_dir: str, filename: str):
    """Write a pandas DataFrame to output_dir/filename, whether output_dir is a
    local path or an s3:// URI (pandas' .to_csv can't write directly to S3)."""
    csv_text = pdf.to_csv(index=False)
    if output_dir.startswith("s3://") or output_dir.startswith("s3a://"):
        import boto3

        bucket, _, prefix = output_dir[output_dir.index("://") + 3 :].partition("/")
        key = f"{prefix.rstrip('/')}/{filename}" if prefix else filename
        boto3.client("s3").put_object(Bucket=bucket, Key=key, Body=csv_text.encode("utf-8"))
    else:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        (out_path / filename).write_text(csv_text, encoding="utf-8")
