"""Big Data implementation: per-user feature engineering (Spark SQL groupBy/agg)
+ K-means clustering via Spark MLlib, following the Transformer/Estimator
Pipeline pattern from the W06 lecture (StringIndexer/VectorAssembler/Scaler ->
Estimator, here VectorAssembler -> StandardScaler -> KMeans).
"""
import argparse
import time
from pathlib import Path

from pyspark.ml import Pipeline
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import StandardScaler, VectorAssembler
from pyspark.sql import functions as F

from common import ORDER_PRODUCTS_SCHEMA, ORDERS_SCHEMA, data_dir, get_spark, read_csv

FEATURE_COLUMNS = [
    "total_orders",
    "avg_basket_size",
    "reorder_rate",
    "avg_days_since_prior_order",
]


def build_user_features(spark, data_dir_: str, n_orders: int | None = None):
    orders = read_csv(spark, data_dir_, "orders.csv", ORDERS_SCHEMA).where(F.col("eval_set") == "prior")
    order_products = read_csv(spark, data_dir_, "order_products__prior.csv", ORDER_PRODUCTS_SCHEMA)

    if n_orders is not None:
        sample_order_ids = order_products.select("order_id").distinct().limit(n_orders)
        order_products = order_products.join(sample_order_ids, on="order_id", how="inner")

    order_aggs = order_products.groupBy("order_id").agg(
        F.count("product_id").alias("item_count"),
        F.sum("reordered").alias("reordered_sum"),
    )

    joined = orders.join(order_aggs, on="order_id", how="inner")

    user_features = joined.groupBy("user_id").agg(
        F.count("order_id").alias("total_orders"),
        F.avg("item_count").alias("avg_basket_size"),
        (F.sum("reordered_sum") / F.sum("item_count")).alias("reorder_rate"),
        F.avg("days_since_prior_order").alias("avg_days_since_prior_order"),
    ).na.drop()

    return user_features


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--n-orders", type=int, default=None)
    parser.add_argument("--n-clusters", type=int, default=4)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent.parent / "output")
    args = parser.parse_args()

    ddir = args.data_dir or data_dir()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    spark = get_spark("instacart-kmeans")

    t0 = time.perf_counter()
    user_features = build_user_features(spark, ddir, n_orders=args.n_orders)
    user_features.cache()
    feature_count = user_features.count()
    t1 = time.perf_counter()

    assembler = VectorAssembler(inputCols=FEATURE_COLUMNS, outputCol="features_raw")
    scaler = StandardScaler(inputCol="features_raw", outputCol="features", withMean=True, withStd=True)
    kmeans = KMeans(featuresCol="features", predictionCol="cluster", k=args.n_clusters, seed=42)
    pipeline = Pipeline(stages=[assembler, scaler, kmeans])

    model = pipeline.fit(user_features)
    result = model.transform(user_features)
    result.cache()
    result.count()
    t2 = time.perf_counter()

    result.select("user_id", *FEATURE_COLUMNS, "cluster").toPandas().to_csv(
        args.output_dir / "kmeans_user_clusters_spark.csv", index=False
    )

    print(f"Users clustered: {feature_count}")
    print(f"Feature engineering time: {t1 - t0:.2f}s")
    print(f"K-means fit + transform time: {t2 - t1:.2f}s")
    print("\nCluster sizes:")
    result.groupBy("cluster").count().orderBy("cluster").show()
    print("Cluster centroids (mean feature values):")
    result.groupBy("cluster").avg(*FEATURE_COLUMNS).orderBy("cluster").show()

    spark.stop()


if __name__ == "__main__":
    main()
