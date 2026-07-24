# Written report (outline)

This report is submitted separately as Word/PDF via eLearn (not graded as part of the GitHub repo). Draft it here, then export.

Sections, following the actual assignment rubric:

1. **Problem introduction** (10%) — the two questions we're answering (frequent co-purchases, customer segmentation), explicitly distinct from Kaggle's original "predict next order" task.
2. **Dataset introduction** (10%) — Instacart Market Basket Analysis, link, structure, size, why it fits.
3. **MapReduce/Spark/SQL approach explanation** (20%) — how FP-Growth and K-means work, the join pipeline, why Spark is needed at this scale.
4. **Output analysis** (20%) — frequent itemsets/association rules found, cluster profiles, and the Big Data vs. non-Big Data performance comparison (runtime/memory at increasing data volumes).
5. **Individual reflection** (20%) — each member writes their own section in `reflections/`, not collaborative.

Code quality (10%) and implementation (10%) are assessed from the GitHub repo itself, not this document.

## Local benchmark (laptop, sample sizes) — for the performance-comparison trend

`benchmark.py` was run locally (laptop, 8GB RAM, Spark in `local[*]` mode — not EMR) across increasing order counts (1K/5K/20K/100K/500K). Full numbers: `../benchmark_results.csv`. Key findings:

- **Spark has a large, roughly constant fixed overhead** (~60–160s per run) at this scale, dominated by JVM/session startup, not data volume — so at small N, pandas/mlxtend/scikit-learn is faster in absolute terms.
- **The non-Big Data implementation's runtime and memory grow with data volume** (FP-Growth: 3.8s/165MB at 1K orders → 34s/2.5GB at 100K orders), while Spark's memory stayed flatter (~1.7–2.5GB) and less sensitive to N.
- **The non-Big Data FP-Growth crashed at 500,000 orders** with `numpy._core._exceptions._ArrayMemoryError: Unable to allocate 21.4 GiB for an array with shape (46049, 500000)`. Root cause: mlxtend's `fpgrowth()` internally densifies the sparse one-hot transaction matrix (`df.values`) before mining, so memory scales as `n_products × n_orders` regardless of sparsity. Spark's FPGrowth at the same 500K orders completed in 147s — it never materializes that matrix, operating on partitioned FP-trees instead. This is the clearest concrete evidence for "what kind of performance" Big Data tooling buys: not raw speed at small scale, but *not falling over* as volume grows.

## Real AWS EMR run (full dataset) — the headline result

Ran on an actual EMR cluster (release emr-7.13.0, Spark 3.5.6, 1 master + 2 core `m5.xlarge`, per Lab 5/6's pattern), against the **full dataset** in S3: all 3,214,874 "prior" orders / 32,434,489 order-product rows, and all 206,209 users. Output CSVs: `../bigdata/output_emr/`.

**Runtime (full dataset, on the 3-node cluster):**
- FP-Growth: **164 seconds** (step start to finish)
- K-means: **58 seconds**

For comparison, our local laptop benchmark took 147s for FP-Growth on just 500K orders (~15% of the full data) before pandas crashed entirely — the real EMR cluster processed **all 3.2M orders** in about the same wall-clock time. This is the clearest possible demonstration of horizontal scaling: more data handled in comparable time by adding cluster capacity, not by a faster single machine.

**Frequent itemsets (top 10, full dataset, minSupport=0.01):**
Banana (472,565 orders, 14.70% support), Bag of Organic Bananas (379,450, 11.80%), Organic Strawberries (264,683, 8.23%), Organic Baby Spinach (241,921, 7.53%), Organic Hass Avocado (213,584, 6.64%), Organic Avocado (176,815, 5.50%), Large Lemon (152,657, 4.75%), Strawberries (142,951, 4.45%), Limes (140,627, 4.37%), Organic Whole Milk (137,905, 4.29%).

**Association rules: 25 found** (vs. 0 at the small local sample — confirms the earlier report note that a full-dataset run would surface real rules). Strongest by lift:
- Organic Raspberries ⇄ Organic Strawberries (lift 3.00)
- Organic Fuji Apple → Banana (lift 2.58)
- Organic Raspberries ⇄ Bag of Organic Bananas (lift 2.50)
- Bag of Organic Bananas ⇄ Organic Hass Avocado (lift 2.47)
- Organic Hass Avocado ⇄ Organic Strawberries (lift 2.32)

**Customer segments (K-means, k=4, all 206,209 users):**

| Cluster | Users | Avg Orders | Avg Basket Size | Reorder Rate | Avg Days Since Prior Order |
|---|---|---|---|---|---|
| 0 | 67,067 | 5.79 | 7.82 | 0.25 | 22.18 |
| 1 | 77,283 | 13.84 | 7.56 | 0.47 | 11.74 |
| 2 | 26,982 | 50.52 | 10.20 | 0.72 | 6.93 |
| 3 | 34,877 | 11.29 | 19.17 | 0.47 | 15.91 |

Cluster 2 stands out at full scale — very frequent shoppers (50.5 average orders, 6.9-day gap, 72% reorder rate) that weren't visible as a distinct group in the small local sample. Cluster 3 is the large-basket segment (19.17 items/order). Cluster 0 is the infrequent/low-reorder segment (22-day gap, lowest reorder rate).

These are the numbers that should replace the local-sample placeholders in report sections 3.4 (System/Cloud Environment — now EMR, not local), 5.1–5.4 (Results and Analysis), and 8.0 (Conclusion).
