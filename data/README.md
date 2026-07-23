# Dataset

**Instacart Market Basket Analysis** (Kaggle, official Instacart 2017 release):
https://www.kaggle.com/c/instacart-market-basket-analysis

Raw CSVs are not committed to this repo (too large for git). Download and place here:

```
data/
├── orders.csv
├── order_products__prior.csv
├── order_products__train.csv
├── products.csv
├── aisles.csv
└── departments.csv
```

For the Big Data pipeline, upload these files to S3/HDFS rather than reading them locally.
