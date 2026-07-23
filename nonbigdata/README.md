# Non-Big Data comparison implementation (local, single machine)

Stack: Python, pandas, mlxtend (association rules), scikit-learn (KMeans). No cluster — runs locally.

Same joins, same FP-Growth-equivalent (mlxtend `fpgrowth`), same K-means, on the same data, for a like-for-like comparison against the `bigdata/` implementation.

## Usage

```
python src/fpgrowth_local.py --n-orders 5000 --min-support 0.02
python src/kmeans_local.py --n-orders 5000 --n-clusters 4
```

Omit `--n-orders` to run on the full dataset (both scripts stream `order_products__prior.csv` in chunks, so the full 32M-row file is never fully loaded into memory at once). Set `INSTACART_DATA_DIR` if the CSVs aren't at the default path (see repo-root `data/README.md`). Output CSVs are written to `output/`.

Wall-clock runtime and memory usage for both implementations, at increasing data volumes, is collected by `../../benchmark.py` (see repo root) to show where the local approach slows down relative to Spark.

- `src/` — `common.py` (data loading helpers), `fpgrowth_local.py`, `kmeans_local.py`
