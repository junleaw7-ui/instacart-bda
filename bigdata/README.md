# Big Data implementation (PySpark MLlib on EMR)

Stack: PySpark MLlib, run on AWS EMR (per Lab 5/6 cluster + spark-submit pattern).

Planned steps:
1. Ingest `orders`, `order_products__prior`, `products` into Spark DataFrames from S3.
2. Join via Spark SQL / DataFrame API.
3. `pyspark.ml.fpm.FPGrowth` on per-order product-id baskets.
4. Engineer per-user features via groupBy/agg (order count, avg basket size, reorder rate, days-between-orders).
5. `pyspark.ml.clustering.KMeans` on the engineered feature vectors.
6. Save frequent itemsets, association rules, and cluster assignments to S3 as Parquet.

Neither FP-Growth nor K-means is covered in the labs — adapt the Transformer/Estimator/Evaluator Pipeline pattern from the W06 lecture (RandomForestClassifier example) using Spark's official docs.

- `notebooks/` — exploratory Spark notebooks
- `src/` — spark-submit scripts (join, fpgrowth, kmeans)
