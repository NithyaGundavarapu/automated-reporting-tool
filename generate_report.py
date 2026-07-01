"""Generates a timestamped Excel summary report from data/ into reports/.

Intended to be run on a schedule (e.g. Windows Task Scheduler) independent of
the live dashboard. See README.md for scheduling instructions.
"""
from datetime import datetime

import pandas as pd

from src.config import REPORTS_DIR
from src.data_loader import load_data
from src.metrics import pick_default_columns, summary_kpis, totals_by_category, trend_by_date


def main():
    df = load_data()
    if df.empty:
        print("No data files found in data/. Nothing to report.")
        return

    date_col, value_col, category_col, _, _ = pick_default_columns(df)
    kpis = summary_kpis(df, value_col)
    trend = trend_by_date(df, date_col, value_col)
    totals = totals_by_category(df, category_col, value_col)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = REPORTS_DIR / f"report_{timestamp}.xlsx"

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        pd.DataFrame([kpis]).to_excel(writer, sheet_name="Summary", index=False)
        if trend is not None:
            trend.to_excel(writer, sheet_name="Trend", index=False)
        if totals is not None:
            totals.to_excel(writer, sheet_name="By Category", index=False)
        df.to_excel(writer, sheet_name="Raw Data", index=False)

    print(f"Report written to {out_path}")


if __name__ == "__main__":
    main()
