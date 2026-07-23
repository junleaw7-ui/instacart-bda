# Dataset

**Instacart Market Basket Analysis** (Kaggle, official Instacart 2017 release):
https://www.kaggle.com/c/instacart-market-basket-analysis

Raw CSVs are not committed to this repo (too large for git). By default, scripts in `bigdata/src/` and `nonbigdata/src/` read from:

```
C:\Users\USER\Desktop\Big Data\Instacart dataset\
├── orders.csv
├── order_products__prior.csv
├── order_products__train.csv
├── products.csv
├── aisles.csv
└── departments.csv
```

Override with the `INSTACART_DATA_DIR` environment variable, or the `--data-dir` CLI flag on each script, if your copy lives elsewhere (e.g. on a teammate's machine, or S3 for the EMR run).

For the Big Data pipeline on EMR, upload these files to S3 and point `--data-dir` at the `s3://` path instead.
