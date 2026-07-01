import pandas as pd


def generate_text_insights(city_df, cuisine_df, price_df, country_df, booking_stats, rest_type_df=None):
    insights = []

    if city_df is not None and not city_df.empty:
        busiest_city = city_df.iloc[0]
        insights.append(
            f"Most restaurants located in: {busiest_city['city']} "
            f"({int(busiest_city['restaurant_count'])} restaurants)"
        )
        if "avg_rating" in city_df.columns:
            best_rated = city_df.dropna(subset=["avg_rating"]).sort_values("avg_rating", ascending=False)
            if not best_rated.empty:
                top = best_rated.iloc[0]
                insights.append(f"Highest-rated city: {top['city']} ({top['avg_rating']:.1f} avg rating)")

    if cuisine_df is not None and not cuisine_df.empty:
        top_cuisine = cuisine_df.iloc[0]
        insights.append(
            f"Most popular cuisine: {top_cuisine['cuisine']} "
            f"({int(top_cuisine['restaurant_count'])} restaurants)"
        )

    if price_df is not None and not price_df.empty:
        premium_row = price_df[price_df["price_range"] == "Premium"]
        if not premium_row.empty:
            insights.append(f"{premium_row.iloc[0]['pct']}% of restaurants are premium-priced")

    if country_df is not None and not country_df.empty and len(country_df) > 1:
        top_country = country_df.iloc[0]
        insights.append(
            f"Most restaurants by country: {top_country['country']} "
            f"({int(top_country['restaurant_count'])} restaurants)"
        )

    if booking_stats:
        if "online_order_pct" in booking_stats:
            insights.append(f"{booking_stats['online_order_pct']}% of restaurants offer online ordering")
        if "book_table_pct" in booking_stats:
            insights.append(f"{booking_stats['book_table_pct']}% of restaurants offer table booking")

    if rest_type_df is not None and not rest_type_df.empty:
        top_type = rest_type_df.iloc[0]
        insights.append(
            f"Most common listing type: {top_type['type']} "
            f"({int(top_type['restaurant_count'])} restaurants)"
        )

    return insights


def check_threshold_alerts(df, booking_stats, thresholds):
    """thresholds: dict with min_avg_rating, min_online_order_pct, min_book_table_pct."""
    alerts = []

    if "rating" in df.columns:
        avg_rating = df["rating"].mean()
        if pd.notna(avg_rating) and avg_rating < thresholds["min_avg_rating"]:
            alerts.append(
                f"Average rating ({avg_rating:.2f}) is below your threshold of "
                f"{thresholds['min_avg_rating']}"
            )

    if booking_stats and "online_order_pct" in booking_stats:
        if booking_stats["online_order_pct"] < thresholds["min_online_order_pct"]:
            alerts.append(
                f"Online order adoption ({booking_stats['online_order_pct']}%) is below your "
                f"threshold of {thresholds['min_online_order_pct']}%"
            )

    if booking_stats and "book_table_pct" in booking_stats:
        if booking_stats["book_table_pct"] < thresholds["min_book_table_pct"]:
            alerts.append(
                f"Table booking adoption ({booking_stats['book_table_pct']}%) is below your "
                f"threshold of {thresholds['min_book_table_pct']}%"
            )

    return alerts
