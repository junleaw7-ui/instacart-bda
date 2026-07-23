# Written report (outline)

This report is submitted separately as Word/PDF via eLearn (not graded as part of the GitHub repo). Draft it here, then export.

Sections, following the actual assignment rubric:

1. **Problem introduction** (10%) — the two questions we're answering (frequent co-purchases, customer segmentation), explicitly distinct from Kaggle's original "predict next order" task.
2. **Dataset introduction** (10%) — Instacart Market Basket Analysis, link, structure, size, why it fits.
3. **MapReduce/Spark/SQL approach explanation** (20%) — how FP-Growth and K-means work, the join pipeline, why Spark is needed at this scale.
4. **Output analysis** (20%) — frequent itemsets/association rules found, cluster profiles, and the Big Data vs. non-Big Data performance comparison (runtime/memory at increasing data volumes).
5. **Individual reflection** (20%) — each member writes their own section in `reflections/`, not collaborative.

Code quality (10%) and implementation (10%) are assessed from the GitHub repo itself, not this document.

## Preliminary local benchmark (for Output analysis section)

`benchmark.py` was run locally (laptop, 8GB RAM, Spark in `local[*]` mode — not EMR) across increasing order counts (1K/5K/20K/100K/500K). Full numbers: `../benchmark_results.csv`. Key findings so far:

- **Spark has a large, roughly constant fixed overhead** (~60–160s per run) at this scale, dominated by JVM/session startup, not data volume — so at small N, pandas/mlxtend/scikit-learn is faster in absolute terms.
- **The non-Big Data implementation's runtime and memory grow with data volume** (FP-Growth: 3.8s/165MB at 1K orders → 34s/2.5GB at 100K orders), while Spark's memory stayed flatter (~1.7–2.5GB) and less sensitive to N.
- **The non-Big Data FP-Growth crashed at 500,000 orders** with `numpy._core._exceptions._ArrayMemoryError: Unable to allocate 21.4 GiB for an array with shape (46049, 500000)`. Root cause: mlxtend's `fpgrowth()` internally densifies the sparse one-hot transaction matrix (`df.values`) before mining, so memory scales as `n_products × n_orders` regardless of sparsity. Spark's FPGrowth at the same 500K orders completed in 147s — it never materializes that matrix, operating on partitioned FP-trees instead. This is the clearest concrete evidence for "what kind of performance" Big Data tooling buys: not raw speed at small scale, but *not falling over* as volume grows.
- These numbers are from a single 8GB laptop in local Spark mode, not a real EMR cluster — re-run `benchmark.py` (or the individual `bigdata/src/*.py` scripts with `--data-dir s3://...`) on EMR with the full ~3.2M orders / 32M order-product rows for the final report numbers. The local run demonstrates the *trend and crossover point*; EMR should be cited for the headline comparison.
