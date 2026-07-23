# Big Data implementation (PySpark MLlib)

Stack: PySpark MLlib. Implemented and tested locally in `local[*]` mode; intended to run on AWS EMR for the final submission (per Lab 5/6 cluster + spark-submit pattern).

Pipeline (`src/fpgrowth_spark.py`, `src/kmeans_spark.py`):
1. Ingest `orders`, `order_products__prior`, `products` into Spark DataFrames.
2. Join / aggregate via the Spark DataFrame API (`groupBy`/`agg`).
3. `pyspark.ml.fpm.FPGrowth` on per-order product-id baskets (`fpgrowth_spark.py`).
4. Engineer per-user features via groupBy/agg (order count, avg basket size, reorder rate, days-between-orders), then `pyspark.ml.clustering.KMeans` via a `Pipeline` (VectorAssembler → StandardScaler → KMeans) (`kmeans_spark.py`) — the Transformer/Estimator pattern from the W06 lecture, adapted since neither FP-Growth nor K-means is covered directly in the labs.

## Usage

```
python src/fpgrowth_spark.py --n-orders 5000 --min-support 0.02
python src/kmeans_spark.py --n-orders 5000 --n-clusters 4
```

Omit `--n-orders` to run on the full dataset. Requires a JDK on `PATH`/`JAVA_HOME` (Java 17 used for local dev) and `INSTACART_DATA_DIR` set if the CSVs aren't at the default path (see repo-root `data/README.md`). Output CSVs (frequent itemsets, rules, cluster assignments) are written to `output/`.

For the EMR run: upload the CSVs to S3, set `--data-dir s3://...`, and submit via `spark-submit` instead of running locally.

- `notebooks/` — exploratory Spark notebooks
- `src/` — the scripts above plus `common.py` (SparkSession/schema helpers)
