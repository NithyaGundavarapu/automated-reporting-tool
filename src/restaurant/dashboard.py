import io
import sys
from datetime import datetime
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from src.restaurant.config import (
    AUTO_REFRESH_SECONDS,
    DATA_DIR,
    DEFAULT_MIN_AVG_RATING,
    DEFAULT_MIN_BOOK_TABLE_PCT,
    DEFAULT_MIN_ONLINE_ORDER_PCT,
)
from src.restaurant.data_loader import load_data
from src.restaurant.insights import check_threshold_alerts, generate_text_insights
from src.restaurant.metrics import (
    booking_delivery_stats,
    city_stats,
    country_stats,
    cuisine_popularity,
    price_range_distribution,
)

st.set_page_config(page_title="Restaurant Analytics Dashboard", layout="wide")

st.title("Restaurant Analytics Dashboard")
st.caption(f"Reading data from `{DATA_DIR}`")

with st.sidebar:
    st.header("Settings")
    auto_refresh = st.toggle("Auto-refresh", value=True)
    interval = st.number_input(
        "Refresh interval (seconds)", min_value=5, value=AUTO_REFRESH_SECONDS, step=5
    )
    if auto_refresh:
        st_autorefresh(interval=interval * 1000, key="auto_refresh_timer")

    st.header("Add data")
    uploaded_files = st.file_uploader(
        "Upload restaurant CSV/Excel files", type=["csv", "xlsx", "xls"], accept_multiple_files=True
    )
    if uploaded_files:
        st.session_state.setdefault("uploaded_restaurant_filenames", set())
        newly_saved = False
        for uploaded in uploaded_files:
            if uploaded.name not in st.session_state.uploaded_restaurant_filenames:
                (DATA_DIR / uploaded.name).write_bytes(uploaded.getbuffer())
                st.session_state.uploaded_restaurant_filenames.add(uploaded.name)
                newly_saved = True
        if newly_saved:
            st.rerun()

    st.header("Alert thresholds")
    min_avg_rating = st.number_input(
        "Minimum average rating", min_value=0.0, max_value=5.0, value=DEFAULT_MIN_AVG_RATING, step=0.1
    )
    min_online_order_pct = st.number_input(
        "Minimum online order adoption (%)", min_value=0.0, max_value=100.0,
        value=DEFAULT_MIN_ONLINE_ORDER_PCT, step=5.0
    )
    min_book_table_pct = st.number_input(
        "Minimum table booking adoption (%)", min_value=0.0, max_value=100.0,
        value=DEFAULT_MIN_BOOK_TABLE_PCT, step=5.0
    )

df = load_data()

if df.empty:
    st.warning(
        f"No data files found in {DATA_DIR}. Drop a restaurant CSV/Excel file there (or use the "
        "uploader in the sidebar) and refresh."
    )
    st.stop()

with st.sidebar:
    st.header("Filters")
    filtered_df = df
    if "city" in df.columns:
        cities = sorted(df["city"].dropna().unique().tolist())
        selected_cities = st.multiselect("Filter by city", cities, default=cities)
        filtered_df = filtered_df[filtered_df["city"].isin(selected_cities)]
    if "country" in df.columns:
        countries = sorted(df["country"].dropna().unique().tolist())
        selected_countries = st.multiselect("Filter by country", countries, default=countries)
        filtered_df = filtered_df[filtered_df["country"].isin(selected_countries)]

city_df = city_stats(filtered_df)
cuisine_df = cuisine_popularity(filtered_df)
price_df = price_range_distribution(filtered_df)
country_df = country_stats(filtered_df)
booking_stats = booking_delivery_stats(filtered_df)

thresholds = {
    "min_avg_rating": min_avg_rating,
    "min_online_order_pct": min_online_order_pct,
    "min_book_table_pct": min_book_table_pct,
}
alerts = check_threshold_alerts(filtered_df, booking_stats, thresholds)
insights = generate_text_insights(city_df, cuisine_df, price_df, country_df, booking_stats)

st.subheader("Alerts")
if alerts:
    for alert in alerts:
        st.warning(alert)
else:
    st.success("All monitored metrics are within your configured thresholds.")

st.subheader("Insights")
if insights:
    for insight in insights:
        st.markdown(f"- {insight}")
else:
    st.info("Not enough data to generate insights yet.")

st.divider()

kpi_cols = st.columns(4)
kpi_cols[0].metric("Total restaurants", f"{len(filtered_df):,}")
kpi_cols[1].metric(
    "Average rating",
    f"{filtered_df['rating'].mean():.2f}" if "rating" in filtered_df.columns else "-",
)
kpi_cols[2].metric(
    "Online order adoption",
    f"{booking_stats['online_order_pct']}%" if booking_stats and "online_order_pct" in booking_stats else "-",
)
kpi_cols[3].metric(
    "Table booking adoption",
    f"{booking_stats['book_table_pct']}%" if booking_stats and "book_table_pct" in booking_stats else "-",
)

st.divider()

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("City-wise restaurant count & average rating")
    if city_df is not None and not city_df.empty:
        fig = px.bar(
            city_df, x="city", y="restaurant_count",
            color="avg_rating" if "avg_rating" in city_df.columns else None,
            color_continuous_scale="RdYlGn",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No city column detected in this dataset.")

with chart_col2:
    st.subheader("Cuisine-wise popularity")
    if cuisine_df is not None and not cuisine_df.empty:
        fig = px.bar(cuisine_df, x="cuisine", y="restaurant_count")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No cuisines column detected in this dataset.")

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("Price range distribution")
    if price_df is not None and not price_df.empty:
        fig = px.pie(price_df, names="price_range", values="pct")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No cost column detected (or not enough distinct values) in this dataset.")

with chart_col4:
    st.subheader("Country-wise restaurant analysis")
    if country_df is not None and not country_df.empty:
        fig = px.bar(
            country_df, x="country", y="restaurant_count",
            color="avg_rating" if "avg_rating" in country_df.columns else None,
            color_continuous_scale="RdYlGn",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No country column detected in this dataset.")

st.divider()
st.subheader("Table booking / online delivery breakdown")
if "city" in filtered_df.columns and ("online_order" in filtered_df.columns or "book_table" in filtered_df.columns):
    agg_dict = {}
    if "online_order" in filtered_df.columns:
        agg_dict["online_order_pct"] = ("online_order", lambda s: round(s.mean() * 100, 1))
    if "book_table" in filtered_df.columns:
        agg_dict["book_table_pct"] = ("book_table", lambda s: round(s.mean() * 100, 1))
    by_city = filtered_df.groupby("city").agg(**agg_dict).reset_index()
    fig = px.bar(by_city, x="city", y=list(agg_dict.keys()), barmode="group")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No online_order/book_table columns detected in this dataset.")

st.divider()
st.subheader("Raw data")
st.dataframe(filtered_df, use_container_width=True)

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    filtered_df.to_excel(writer, sheet_name="Filtered Data", index=False)

download_col1, download_col2 = st.columns(2)
download_col1.download_button(
    "Download filtered data (CSV)",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="restaurant_filtered_data.csv",
    mime="text/csv",
)
download_col2.download_button(
    "Download filtered data (Excel)",
    data=excel_buffer.getvalue(),
    file_name="restaurant_filtered_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
