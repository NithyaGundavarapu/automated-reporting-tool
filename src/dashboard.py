import sys
from datetime import datetime
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from src.config import AUTO_REFRESH_SECONDS, DATA_DIR
from src.data_loader import load_data
from src.metrics import pick_default_columns, summary_kpis, totals_by_category, trend_by_date

st.set_page_config(page_title="Automated Reporting Tool", layout="wide")

st.title("Automated Reporting Tool")
st.caption(f"Reading data from `{DATA_DIR}`")

with st.sidebar:
    st.header("Settings")
    auto_refresh = st.toggle("Auto-refresh", value=True)
    interval = st.number_input(
        "Refresh interval (seconds)", min_value=5, value=AUTO_REFRESH_SECONDS, step=5
    )
    if auto_refresh:
        st_autorefresh(interval=interval * 1000, key="auto_refresh_timer")

df = load_data()

if df.empty:
    st.warning(f"No data files found in {DATA_DIR}. Add a .csv or .xlsx file and refresh.")
    st.stop()

date_col, value_col, category_col, numeric_cols, category_cols = pick_default_columns(df)

with st.sidebar:
    st.header("Filters")
    value_col = st.selectbox(
        "Value column", numeric_cols, index=numeric_cols.index(value_col) if value_col in numeric_cols else 0
    )
    category_col = st.selectbox(
        "Category column",
        ["(none)"] + category_cols,
        index=(category_cols.index(category_col) + 1) if category_col in category_cols else 0,
    )
    category_col = None if category_col == "(none)" else category_col

    filtered_df = df
    if date_col:
        min_date, max_date = df[date_col].min(), df[date_col].max()
        date_range = st.date_input("Date range", value=(min_date.date(), max_date.date()))
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start, end = date_range
            filtered_df = filtered_df[
                (filtered_df[date_col] >= pd.Timestamp(start))
                & (filtered_df[date_col] <= pd.Timestamp(end))
            ]

    if category_col:
        options = sorted(df[category_col].dropna().unique().tolist())
        selected = st.multiselect("Filter by " + category_col, options, default=options)
        filtered_df = filtered_df[filtered_df[category_col].isin(selected)]

kpis = summary_kpis(filtered_df, value_col)
col1, col2, col3 = st.columns(3)
col1.metric("Total records", f"{kpis['total_records']:,}")
col2.metric(f"Total {value_col}", f"{kpis['total']:,.2f}" if kpis["total"] is not None else "-")
col3.metric(f"Average {value_col}", f"{kpis['average']:,.2f}" if kpis["average"] is not None else "-")

st.divider()

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Trend over time")
    trend = trend_by_date(filtered_df, date_col, value_col)
    if trend is not None and not trend.empty:
        fig = px.line(trend, x=date_col, y=value_col, markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No date column detected for a trend chart.")

with chart_col2:
    st.subheader(f"Totals by {category_col or 'category'}")
    totals = totals_by_category(filtered_df, category_col, value_col)
    if totals is not None and not totals.empty:
        fig = px.bar(totals, x=category_col, y=value_col)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category column detected for a breakdown chart.")

st.divider()
st.subheader("Raw data")
st.dataframe(filtered_df, use_container_width=True)

st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
