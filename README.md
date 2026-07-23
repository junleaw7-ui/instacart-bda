# Instacart Big Data Analytics — IST3134 Group Assignment

Group assignment for IST3134 Big Data Analytics in the Cloud (Sunway University), 20% of final grade, due 10–13 Aug 2026.

## Problem

Using the [Instacart Market Basket Analysis](https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis) dataset (orders, order-products, products — 32M+ order-product rows), we answer two questions of our own framing (not Kaggle's original "predict next reorder" task):

1. **Which products are most frequently purchased together?** — FP-Growth / association rule mining over per-order product baskets.
2. **Can customers be grouped into distinct shopping behavior segments?** — K-means clustering over engineered per-user features (order count, avg basket size, reorder rate, days-between-orders).

Both are unsupervised; no labeled target variable is used.

## Repo layout

- `data/` — dataset download instructions (raw CSVs are not committed; see `data/README.md`)
- `bigdata/` — PySpark MLlib implementation (FP-Growth + K-means), intended to run on AWS EMR
- `nonbigdata/` — local single-machine comparison (pandas + mlxtend + scikit-learn)
- `report/` — outline/draft for the written report, exported separately as Word/PDF and submitted via eLearn (not part of the GitHub-graded code)
- `reflections/` — individual reflections, one file per team member (not collaborative)

## Grading rubric (from the actual assignment brief)

| Section | Weight |
|---|---|
| Problem introduction | 10% |
| Dataset introduction | 10% |
| MapReduce/Spark/SQL approach explanation | 20% |
| Output analysis | 20% |
| Individual reflection | 20% |
| Code quality | 10% |
| Implementation | 10% |

## Setup (local dev/testing)

1. Download the dataset (see `data/README.md`) and set `INSTACART_DATA_DIR` if it's not at the default path.
2. `pip install -r requirements.txt`
3. PySpark needs a JDK (17 was used for local dev) — install one and set `JAVA_HOME`/`PATH` before running anything in `bigdata/`.
4. Run an implementation directly, e.g.:
   ```
   python nonbigdata/src/fpgrowth_local.py --n-orders 5000 --min-support 0.02
   python bigdata/src/fpgrowth_spark.py --n-orders 5000 --min-support 0.02
   ```
   Both accept `--n-orders` to run on a subsample; omit it to run on the full dataset.
5. `python benchmark.py` runs both implementations across increasing `--n-orders` scales and writes timing/memory results to `benchmark_results.csv`. Note: this runs Spark in `local[*]` mode on a laptop, not EMR — it shows the scaling trend, not final cluster-scale numbers. Re-run the Big Data side on EMR with the full data for the report's performance comparison.

## Submission

- Code + dataset link → GitHub (this repo)
- Written report (Word/PDF) → submitted separately via eLearn
- Instructor confirmation of dataset/problem choice: due 24 Jul 2026
