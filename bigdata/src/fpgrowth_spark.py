"""Big Data implementation: frequent itemset / association rule mining via
Spark MLlib FP-Growth, distributed join across orders/order_products/products.

Adapted from the Transformer/Estimator Pipeline pattern (W06 lecture) --
FPGrowth is an Estimator whose .fit() produces an FPGrowthModel with
freqItemsets and associationRules attributes.
"""
import argparse
import time
from pathlib import Path

from pyspark.ml.fpm import FPGrowth
from pyspark.sql import functions as F

from common import ORDER_PRODUCTS_SCHEMA, PRODUCTS_SCHEMA, data_dir, get_spark, read_csv


def build_baskets(spark, data_dir_: str, n_orders: int | None = None):
    order_products = read_csv(spark, data_dir_, "order_products__prior.csv", ORDER_PRODUCTS_SCHEMA)

    if n_orders is not None:
        sample_order_ids = (
            order_products.select("order_id").distinct().limit(n_orders)
        )
        order_products = order_products.join(sample_order_ids, on="order_id", how="inner")

    baskets = (
        order_products.groupBy("order_id")
        .agg(F.collect_set("product_id").alias("items"))
        .select("items")
    )
    return baskets


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--n-orders", type=int, default=None)
    parser.add_argument("--min-support", type=float, default=0.01)
    parser.add_argument("--min-confidence", type=float, default=0.1)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent.parent / "output")
    args = parser.parse_args()

    ddir = args.data_dir or data_dir()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    spark = get_spark("instacart-fpgrowth")

    t0 = time.perf_counter()
    baskets = build_baskets(spark, ddir, n_orders=args.n_orders)
    basket_count = baskets.count()
    t1 = time.perf_counter()

    fp = FPGrowth(itemsCol="items", minSupport=args.min_support, minConfidence=args.min_confidence)
    model = fp.fit(baskets)
    freq_itemsets = model.freqItemsets
    rules = model.associationRules
    freq_itemsets.count()
    rules.count()
    t2 = time.perf_counter()

    products = read_csv(spark, ddir, "products.csv", PRODUCTS_SCHEMA).select("product_id", "product_name")
    products_map = {row["product_id"]: row["product_name"] for row in products.collect()}

    def name_ids(ids):
        return ", ".join(products_map.get(i, str(i)) for i in ids)

    itemsets_pdf = freq_itemsets.orderBy(F.desc("freq")).toPandas()
    itemsets_pdf["items_named"] = itemsets_pdf["items"].apply(name_ids)
    itemsets_pdf.to_csv(args.output_dir / "fpgrowth_itemsets_spark.csv", index=False)

    rules_pdf = rules.toPandas()
    rules_pdf["antecedent_named"] = rules_pdf["antecedent"].apply(name_ids)
    rules_pdf["consequent_named"] = rules_pdf["consequent"].apply(name_ids)
    rules_pdf.to_csv(args.output_dir / "fpgrowth_rules_spark.csv", index=False)

    print(f"Baskets: {basket_count}")
    print(f"Basket build time: {t1 - t0:.2f}s")
    print(f"FP-Growth fit + rules time: {t2 - t1:.2f}s")
    print(f"Frequent itemsets found: {freq_itemsets.count()}")
    print(f"Association rules found: {rules.count()}")

    spark.stop()


if __name__ == "__main__":
    main()
