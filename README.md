# Instacart Big Data Analytics — IST3134 Group Assignment

Group assignment for IST3134 Big Data Analytics in the Cloud (Sunway University).

## Problem

Using the [Instacart Market Basket Analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis) dataset (orders, order-products, products — 32M+ order-product rows), we answer two questions of our own framing (not Kaggle's original "predict next reorder" task):

1. **Which products are most frequently purchased together?** — FP-Growth / association rule mining over per-order product baskets.
2. **Can customers be grouped into distinct shopping behavior segments?** — K-means clustering over engineered per-user features (order count, avg basket size, reorder rate, days-between-orders).

Both are unsupervised; no labeled target variable is used.

## Repo layout

- `data/` — dataset download instructions (raw CSVs are not committed; see `data/README.md`)
- `bigdata/` — PySpark MLlib implementation (FP-Growth + K-means); tested locally and validated with a real run on AWS EMR (see `bigdata/output_emr/` for those results)
- `nonbigdata/` — local single-machine comparison (pandas + mlxtend + scikit-learn)
- `benchmark.py`, `benchmark_results.csv` — runtime/memory comparison between the two implementations across increasing data volumes

## Setup (local dev/testing)

1. Download the dataset and set `INSTACART_DATA_DIR` to point at it (see `data/README.md` — don't rely on the fallback default, it's a personal path).
2. `pip install -r requirements.txt`
3. PySpark needs a JDK (17 was used for local dev) — install one and set `JAVA_HOME`/`PATH` before running anything in `bigdata/`. Also set `SPARK_MASTER=local[*]` for local runs — `bigdata/src/common.py` leaves Spark's master unset otherwise, so that on EMR `spark-submit --master yarn` (not a hardcoded `local[*]`) actually controls where the job runs.
4. Run an implementation directly, e.g.:
   ```
   python nonbigdata/src/fpgrowth_local.py --n-orders 5000 --min-support 0.02
   python bigdata/src/fpgrowth_spark.py --n-orders 5000 --min-support 0.02
   ```
   Both accept `--n-orders` to run on a subsample; omit it to run on the full dataset.
5. `python benchmark.py` runs both implementations across increasing `--n-orders` scales and writes timing/memory results to `benchmark_results.csv`. Note: this runs Spark in `local[*]` mode on a laptop, not EMR — it shows the scaling trend, not the full-scale numbers. The full-dataset EMR run has already been done (see `bigdata/output_emr/` for those results); to reproduce it, see the EMR launch example in `bigdata/README.md`.
