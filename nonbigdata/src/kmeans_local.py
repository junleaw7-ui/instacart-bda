"""Non-Big Data comparison: per-user feature engineering + K-means clustering.

Segments Instacart customers into shopping-behavior clusters (e.g. bulk weekly
shoppers vs. small frequent buyers) using pandas + scikit-learn on a single machine.
"""
import argparse
import time
from pathlib import Path

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from common import data_dir, iter_order_products_prior_chunks, load_orders

FEATURE_COLUMNS = [
    "total_orders",
    "avg_basket_size",
    "reorder_rate",
    "avg_days_since_prior_order",
]


def build_order_aggregates(data_dir_: Path, nrows: int | None = None, n_orders: int | None = None) -> pd.DataFrame:
    """Per-order item count and reordered-sum, computed via chunked streaming
    so the full 32M-row order_products__prior.csv is never held in memory at once.

    n_orders limits to the first N distinct order_ids encountered (for an
    apples-to-apples comparison against the Spark/order-count-based scripts);
    nrows limits to the first N raw CSV rows (faster, approximate)."""
    partials = []
    seen_orders: set[int] = set()
    for chunk in iter_order_products_prior_chunks(data_dir_, nrows=nrows):
        if n_orders is not None:
            seen_orders.update(chunk["order_id"].unique().tolist())
            if len(seen_orders) > n_orders:
                keep_ids = set(sorted(seen_orders)[:n_orders])
                chunk = chunk[chunk["order_id"].isin(keep_ids)]
        agg = chunk.groupby("order_id", sort=False).agg(
            item_count=("product_id", "count"),
            reordered_sum=("reordered", "sum"),
        )
        partials.append(agg)
        if n_orders is not None and len(seen_orders) >= n_orders:
            break
    combined = pd.concat(partials)
    result = combined.groupby(level=0).sum()
    if n_orders is not None:
        result = result.loc[sorted(result.index)[:n_orders]]
    return result


def build_user_features(data_dir_: Path, nrows: int | None = None, n_orders: int | None = None) -> pd.DataFrame:
    order_aggs = build_order_aggregates(data_dir_, nrows=nrows, n_orders=n_orders)

    orders = load_orders(data_dir_)
    prior_orders = orders[orders["eval_set"] == "prior"].set_index("order_id")

    joined = prior_orders.join(order_aggs, how="inner")

    user_features = joined.groupby("user_id").agg(
        total_orders=("item_count", "count"),
        avg_basket_size=("item_count", "mean"),
        reorder_rate_num=("reordered_sum", "sum"),
        reorder_rate_den=("item_count", "sum"),
        avg_days_since_prior_order=("days_since_prior_order", "mean"),
    )
    user_features["reorder_rate"] = (
        user_features["reorder_rate_num"] / user_features["reorder_rate_den"]
    )
    return user_features[FEATURE_COLUMNS].dropna()


def run_kmeans(user_features: pd.DataFrame, n_clusters: int = 4, random_state: int = 42):
    scaler = StandardScaler()
    X = scaler.fit_transform(user_features[FEATURE_COLUMNS])

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    labels = model.fit_predict(X)

    result = user_features.copy()
    result["cluster"] = labels
    return result, model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=None)
    parser.add_argument("--nrows", type=int, default=None, help="Limit raw rows read from order_products__prior.csv (fast, approximate)")
    parser.add_argument("--n-orders", type=int, default=None, help="Limit to first N distinct orders (for apples-to-apples benchmarking against Spark scripts)")
    parser.add_argument("--n-clusters", type=int, default=4)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent.parent / "output")
    args = parser.parse_args()

    ddir = args.data_dir or data_dir()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    user_features = build_user_features(ddir, nrows=args.nrows, n_orders=args.n_orders)
    t1 = time.perf_counter()
    result, model = run_kmeans(user_features, n_clusters=args.n_clusters)
    t2 = time.perf_counter()

    result.to_csv(args.output_dir / "kmeans_user_clusters.csv")

    print(f"Users clustered: {len(result)}")
    print(f"Feature engineering time: {t1 - t0:.2f}s")
    print(f"K-means fit time: {t2 - t1:.2f}s")
    print("\nCluster sizes:")
    print(result["cluster"].value_counts().sort_index())
    print("\nCluster centroids (mean feature values):")
    print(result.groupby("cluster")[FEATURE_COLUMNS].mean())


if __name__ == "__main__":
    main()
