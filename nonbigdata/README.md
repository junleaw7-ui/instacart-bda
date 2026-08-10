# Non-Big Data comparison implementation (local, single machine)

Stack: Python, pandas, mlxtend (association rules), scikit-learn (KMeans). No cluster — runs locally.

Same joins, same FP-Growth-equivalent (mlxtend `fpgrowth`), same K-means, on the same data, for a like-for-like comparison against the `bigdata/` implementation.

## Usage

```
python src/fpgrowth_local.py --n-orders 5000 --min-support 0.02
python src/kmeans_local.py --n-orders 5000 --n-clusters 4
```

Omit `--n-orders` to run on the full dataset. `kmeans_local.py` always streams `order_products__prior.csv` in chunks, so it never loads the full 32M-row file into memory at once. `fpgrowth_local.py` only chunks when `--n-orders` is passed for sampling; omitting it (the full-dataset run) reads the whole file in one `pd.read_csv()` call, which is the actual memory bottleneck for that script at full scale. Set `INSTACART_DATA_DIR` if the CSVs aren't at the default path (see repo-root `data/README.md`). Output CSVs are written to `output/`.

Wall-clock runtime and memory usage for both implementations, at increasing data volumes, is collected by `../benchmark.py` (see repo root) to show where the local approach slows down relative to Spark.

- `src/` — `common.py` (data loading helpers), `fpgrowth_local.py`, `kmeans_local.py`
