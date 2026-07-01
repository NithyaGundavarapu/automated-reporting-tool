import pandas as pd


def city_stats(df):
    if "city" not in df.columns:
        return None
    if "rating" in df.columns:
        grouped = df.groupby("city").agg(
            restaurant_count=("city", "size"), avg_rating=("rating", "mean")
        )
    else:
        grouped = df.groupby("city").agg(restaurant_count=("city", "size"))
    return grouped.sort_values("restaurant_count", ascending=False).reset_index()


def cuisine_popularity(df, top_n=10):
    if "cuisines" not in df.columns:
        return None
    exploded = (
        df["cuisines"]
        .dropna()
        .str.split(",")
        .explode()
        .str.strip()
    )
    exploded = exploded[exploded.ne("") & exploded.ne("nan")]
    if exploded.empty:
        return None
    counts = exploded.value_counts().head(top_n).reset_index()
    counts.columns = ["cuisine", "restaurant_count"]
    return counts


def price_range_distribution(df):
    if "cost" not in df.columns:
        return None
    costs = df["cost"].dropna()
    if costs.nunique() < 3:
        return None
    buckets = pd.qcut(costs, q=3, labels=["Budget", "Mid-range", "Premium"], duplicates="drop")
    dist = (buckets.value_counts(normalize=True) * 100).round(1).reset_index()
    dist.columns = ["price_range", "pct"]
    order = {"Budget": 0, "Mid-range": 1, "Premium": 2}
    dist["__order"] = dist["price_range"].map(order)
    return dist.sort_values("__order").drop(columns="__order").reset_index(drop=True)


def country_stats(df):
    if "country" not in df.columns:
        return None
    if "rating" in df.columns:
        grouped = df.groupby("country").agg(
            restaurant_count=("country", "size"), avg_rating=("rating", "mean")
        )
    else:
        grouped = df.groupby("country").agg(restaurant_count=("country", "size"))
    return grouped.sort_values("restaurant_count", ascending=False).reset_index()


def booking_delivery_stats(df):
    stats = {}
    if "online_order" in df.columns:
        stats["online_order_pct"] = round(df["online_order"].mean() * 100, 1)
    if "book_table" in df.columns:
        stats["book_table_pct"] = round(df["book_table"].mean() * 100, 1)
    return stats if stats else None
