# Instacart Big Data Analytics — IST3134 Group Assignment

Group assignment for IST3134 Big Data Analytics in the Cloud (Sunway University), 20% of final grade, due 10–13 Aug 2026.

## Problem

Using the [Instacart Market Basket Analysis](https://www.kaggle.com/c/instacart-market-basket-analysis) dataset (orders, order-products, products — 32M+ order-product rows), we answer two questions of our own framing (not Kaggle's original "predict next reorder" task):

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

## Submission

- Code + dataset link → GitHub (this repo)
- Written report (Word/PDF) → submitted separately via eLearn
- Instructor confirmation of dataset/problem choice: due 24 Jul 2026
