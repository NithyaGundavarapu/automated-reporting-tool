import io
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
from src.metrics import (
    pick_default_columns,
    previous_period_kpis,
    summary_kpis,
    totals_by_category,
    trend_by_date,
)

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

    st.header("Add data")
    uploaded_files = st.file_uploader(
        "Upload CSV/Excel files", type=["csv", "xlsx", "xls"], accept_multiple_files=True
    )
    if uploaded_files:
        st.session_state.setdefault("uploaded_filenames", set())
        newly_saved = False
        for uploaded in uploaded_files:
            if uploaded.name not in st.session_state.uploaded_filenames:
                (DATA_DIR / uploaded.name).write_bytes(uploaded.getbuffer())
                st.session_state.uploaded_filenames.add(uploaded.name)
                newly_saved = True
        if newly_saved:
            st.rerun()

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
    period_start, period_end = None, None
    if date_col:
        min_date, max_date = df[date_col].min(), df[date_col].max()
        date_range = st.date_input("Date range", value=(min_date.date(), max_date.date()))
        if isinstance(date_range, tuple) and len(date_range) == 2:
            period_start, period_end = date_range
            filtered_df = filtered_df[
                (filtered_df[date_col] >= pd.Timestamp(period_start))
                & (filtered_df[date_col] <= pd.Timestamp(period_end))
            ]

    if category_col:
        options = sorted(df[category_col].dropna().unique().tolist())
        selected = st.multiselect("Filter by " + category_col, options, default=options)
        filtered_df = filtered_df[filtered_df[category_col].isin(selected)]


def _delta(current, previous):
    if previous in (None, 0) or current is None:
        return None
    return f"{(current - previous) / previous:+.1%} vs prior period"


kpis = summary_kpis(filtered_df, value_col)
prev_kpis = (
    previous_period_kpis(df, date_col, value_col, period_start, period_end)
    if period_start and period_end
    else None
)

col1, col2, col3 = st.columns(3)
col1.metric(
    "Total records",
    f"{kpis['total_records']:,}",
    delta=_delta(kpis["total_records"], prev_kpis["total_records"]) if prev_kpis else None,
)
col2.metric(
    f"Total {value_col}",
    f"{kpis['total']:,.2f}" if kpis["total"] is not None else "-",
    delta=_delta(kpis["total"], prev_kpis["total"]) if prev_kpis else None,
)
col3.metric(
    f"Average {value_col}",
    f"{kpis['average']:,.2f}" if kpis["average"] is not None else "-",
    delta=_delta(kpis["average"], prev_kpis["average"]) if prev_kpis else None,
)
if prev_kpis:
    st.caption("Delta compares the selected date range to the immediately preceding period of equal length.")

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

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    filtered_df.to_excel(writer, sheet_name="Filtered Data", index=False)

download_col1, download_col2 = st.columns(2)
download_col1.download_button(
    "Download filtered data (CSV)",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_data.csv",
    mime="text/csv",
)
download_col2.download_button(
    "Download filtered data (Excel)",
    data=excel_buffer.getvalue(),
    file_name="filtered_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
