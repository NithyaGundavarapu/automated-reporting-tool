# Automated Reporting Tool

A local BI dashboard that reads Excel/CSV files from `data/`, shows KPIs and charts, and
auto-refreshes on an interval. Includes a companion script for generating scheduled Excel report
snapshots.

## Setup

```
pip install -r requirements.txt
```

## Run the live dashboard

```
streamlit run src\dashboard.py
```

or double-click `run_dashboard.bat`. It opens in your browser. Use the sidebar to toggle
auto-refresh, change the refresh interval, pick which columns to chart, and filter by date/category.

## Add your own data

Drop any `.csv` or `.xlsx` file into `data/`. The dashboard automatically:
- combines all files in that folder
- detects a date column (for the trend chart)
- detects numeric columns (for KPIs/values — pick which one in the sidebar)
- detects category columns (for the breakdown chart/filter)

Remove or replace `data/sample_sales.csv` once you have real data — it's just there so the
dashboard has something to show immediately.

## Generate a scheduled report snapshot

```
python generate_report.py
```

Writes a timestamped `report_YYYYMMDD_HHMMSS.xlsx` to `reports/` with a Summary, Trend, By
Category, and Raw Data sheet.

To run this automatically on a schedule:
1. Open **Task Scheduler** on Windows.
2. Create a new task, trigger set to your desired frequency (e.g. daily).
3. Action: **Start a program**, program = path to `python.exe`, arguments =
   `"C:\Users\gunda\OneDrive\Desktop\automated reprting tool\generate_report.py"`,
   start-in = `C:\Users\gunda\OneDrive\Desktop\automated reprting tool`.
