# Dataset

**Instacart Market Basket Analysis** (Kaggle, official Instacart 2017 release):
https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis

Raw CSVs are not committed to this repo (too large for git). Download the 6 files:

```
orders.csv
order_products__prior.csv
order_products__train.csv
products.csv
aisles.csv
departments.csv
```

and put them in one folder, then **tell the scripts where that folder is** — either:
- set the `INSTACART_DATA_DIR` environment variable to that folder's path, or
- pass `--data-dir <path>` on every script invocation

**Note for anyone other than the original author:** the scripts fall back to a hardcoded default path (`C:\Users\USER\Desktop\Big Data\Instacart dataset`) if neither of the above is set — that's the original author's personal machine, not a placeholder you should try to match. Always set `INSTACART_DATA_DIR` (or `--data-dir`) yourself; don't rely on the default.

For the Big Data pipeline on EMR, upload these files to S3 and point `--data-dir` at the `s3://` path instead.
