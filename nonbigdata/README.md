# Non-Big Data comparison implementation (local, single machine)

Stack: Python, pandas, mlxtend (association rules), scikit-learn (KMeans). No cluster — runs locally.

Same joins, same FP-Growth-equivalent (mlxtend `fpgrowth`/`apriori`), same K-means, on the same data, for a like-for-like comparison against the `bigdata/` implementation.

Collect wall-clock runtime and/or memory usage for the join + each algorithm, ideally at increasing data volumes (subsample vs. full `order_products__prior.csv`) to show where the local approach slows down relative to Spark.

- `src/` — local equivalent scripts (join, fpgrowth, kmeans, benchmarking)
