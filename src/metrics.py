import pandas as pd

from src.data_loader import detect_category_columns, detect_date_column, detect_numeric_columns


def summary_kpis(df, value_col):
    return {
        "total_records": len(df),
        "total": df[value_col].sum() if value_col else None,
        "average": df[value_col].mean() if value_col else None,
    }


def previous_period_kpis(df, date_col, value_col, start, end):
    """KPIs for the period of equal length immediately preceding [start, end]."""
    if not date_col or not value_col:
        return None
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    period_length = end - start
    prev_end = start - pd.Timedelta(days=1)
    prev_start = prev_end - period_length
    prev_df = df[(df[date_col] >= prev_start) & (df[date_col] <= prev_end)]
    return summary_kpis(prev_df, value_col)


def trend_by_date(df, date_col, value_col, freq="W"):
    if not date_col or not value_col:
        return None
    series = (
        df.dropna(subset=[date_col])
        .set_index(date_col)[value_col]
        .resample(freq)
        .sum()
        .reset_index()
    )
    return series


def totals_by_category(df, category_col, value_col):
    if not category_col or not value_col:
        return None
    return (
        df.groupby(category_col, dropna=False)[value_col]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def pick_default_columns(df):
    date_col = detect_date_column(df)
    numeric_cols = detect_numeric_columns(df)
    category_cols = detect_category_columns(df)
    value_col = numeric_cols[0] if numeric_cols else None
    category_col = category_cols[0] if category_cols else None
    return date_col, value_col, category_col, numeric_cols, category_cols
