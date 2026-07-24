# Big Data implementation (PySpark MLlib)

Stack: PySpark MLlib. Developed/tested locally in `local[*]` mode, then run for real on AWS EMR (release emr-7.13.0, Spark 3.5.6, 1 master + 2 core `m5.xlarge`, per Lab 5/6's cluster + spark-submit pattern) against the full dataset in S3 — see `output_emr/` for the real results and `../report/README.md` for the write-up.

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

For an EMR run: upload the CSVs and `src/*.py` to S3, then launch a cluster with both scripts as EMR Steps, e.g.:
```
aws emr create-cluster --name instacart-bda --release-label emr-7.13.0 \
  --applications Name=Hadoop Name=Spark \
  --ec2-attributes KeyName=vockey,SubnetId=<subnet>,InstanceProfile=EMR_EC2_DefaultRole \
  --service-role EMR_DefaultRole \
  --instance-groups InstanceGroupType=MASTER,InstanceCount=1,InstanceType=m5.xlarge \
                     InstanceGroupType=CORE,InstanceCount=2,InstanceType=m5.xlarge \
  --auto-terminate \
  --steps '[{"Type":"CUSTOM_JAR","Jar":"command-runner.jar","ActionOnFailure":"CONTINUE",
    "Args":["spark-submit","--py-files","s3://<bucket>/scripts/common.py",
    "s3://<bucket>/scripts/fpgrowth_spark.py","--data-dir","s3://<bucket>/data",
    "--output-dir","s3://<bucket>/output"]}, ...]'
```
`--auto-terminate` shuts the cluster down as soon as the steps finish, so it doesn't idle and rack up cost. `common.py`'s `save_csv()` writes directly to S3 via boto3 when `--output-dir` is an `s3://` URI.

- `notebooks/` — exploratory Spark notebooks
- `src/` — the scripts above plus `common.py` (SparkSession/schema helpers)
- `output_emr/` — real output from the full-dataset EMR run (committed, not regenerable-and-ignored like `output/`)
