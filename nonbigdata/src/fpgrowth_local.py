"""Non-Big Data comparison: frequent itemset / association rule mining.

Finds products frequently purchased together using pandas + mlxtend on a
single machine (no cluster). Equivalent task to bigdata/src/fpgrowth_spark.py.
"""
import argparse
import time
from pathlib import Path

import pandas as pd
from mlxtend.frequent_patterns import association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder

from common import data_dir, load_products


def load_baskets(data_dir_: Path, n_orders: int | None = None) -> list[list[int]]:
    """One basket (list of product_ids) per order_id, read directly off
    order_products__prior.csv without loading the whole 32M-row file."""
    usecols = ["order_id", "product_id"]
    dtypes = {"order_id": "int32", "product_id": "int32"}

    if n_orders is None:
        df = pd.read_csv(data_dir_ / "order_products__prior.csv", usecols=usecols, dtype=dtypes)
    else:
        # Read incrementally until we've seen n_orders distinct order_ids.
        chunks = []
        seen_orders = set()
        for chunk in pd.read_csv(
            data_dir_ / "order_products__prior.csv", usecols=usecols, dtype=dtypes, chunksize=1_000_000
        ):
            chunks.append(chunk)
            seen_orders.update(chunk["order_id"].unique())
            if len(seen_orders) >= n_orders:
                break
        df = pd.concat(chunks)
        keep_orders = sorted(seen_orders)[:n_orders]
        df = df[df["order_id"].isin(keep_orders)]

    return df.groupby("order_id")["product_id"].apply(list).tolist()


def mine_frequent_itemsets(baskets: list[list[int]], min_support: float = 0.01):
    encoder = TransactionEncoder()
    encoded_array = encoder.fit(baskets).transform(baskets, sparse=True)
    column_names = [str(c) for c in encoder.columns_]
    encoded_df = pd.DataFrame.sparse.from_spmatrix(encoded_array, columns=column_names)

    itemsets = fpgrowth(encoded_df, min_support=min_support, use_colnames=True)
    rules = association_rules(itemsets, metric="lift", min_threshold=1.0)

    # column names were stringified for mlxtend; cast back to int product_ids
    itemsets["itemsets"] = itemsets["itemsets"].apply(lambda s: frozenset(int(x) for x in s))
    rules["antecedents"] = rules["antecedents"].apply(lambda s: frozenset(int(x) for x in s))
    rules["consequents"] = rules["consequents"].apply(lambda s: frozenset(int(x) for x in s))
    return itemsets, rules


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--n-orders", type=int, default=None, help="Limit number of order baskets (for sampling/benchmarking)")
    parser.add_argument("--min-support", type=float, default=0.01)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent.parent / "output")
    args = parser.parse_args()

    ddir = args.data_dir or data_dir()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    baskets = load_baskets(ddir, n_orders=args.n_orders)
    t1 = time.perf_counter()
    itemsets, rules = mine_frequent_itemsets(baskets, min_support=args.min_support)
    t2 = time.perf_counter()

    products = load_products(ddir).set_index("product_id")["product_name"]

    def name_itemset(frozenset_ids):
        return ", ".join(products.get(pid, str(pid)) for pid in frozenset_ids)

    itemsets = itemsets.sort_values("support", ascending=False)
    itemsets["items_named"] = itemsets["itemsets"].apply(name_itemset)
    rules["antecedents_named"] = rules["antecedents"].apply(name_itemset)
    rules["consequents_named"] = rules["consequents"].apply(name_itemset)

    itemsets.to_csv(args.output_dir / "fpgrowth_itemsets.csv", index=False)
    rules.to_csv(args.output_dir / "fpgrowth_rules.csv", index=False)

    print(f"Baskets: {len(baskets)}")
    print(f"Basket loading time: {t1 - t0:.2f}s")
    print(f"FP-Growth + rules time: {t2 - t1:.2f}s")
    print(f"Frequent itemsets found: {len(itemsets)}")
    print(f"Association rules found: {len(rules)}")
    print("\nTop 10 frequent itemsets:")
    print(itemsets[["items_named", "support"]].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
