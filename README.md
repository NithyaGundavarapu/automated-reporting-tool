# Automated Reporting Tool

Two local BI dashboards:
- **Sales dashboard** (`src/dashboard.py`, port 8501) — generic Excel/CSV KPI dashboard.
- **Restaurant analytics dashboard** (`src/restaurant/dashboard.py`, port 8502) — Zomato-style
  restaurant data analysis. See [Restaurant Analytics Dashboard](#restaurant-analytics-dashboard)
  below.

Both auto-refresh on an interval and support uploading files directly from the sidebar. The sales
dashboard also has a companion script for generating scheduled Excel report snapshots.

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

## Restaurant Analytics Dashboard

A dedicated dashboard (`src/restaurant/dashboard.py`) for Zomato-style restaurant data, covering:
- City-wise restaurant count & average rating
- Cuisine-wise popularity (most common cuisines)
- Price range distribution (Budget / Mid-range / Premium %)
- Country-wise restaurant analysis (shown only if a country column is present)
- Table booking / online delivery adoption, overall and by city
- Auto-generated text insights (e.g. "Highest-rated city: X") and threshold-based alerts
  (e.g. warns if average rating or online-order adoption drops below a level you set in the sidebar)

### Run it

```
streamlit run src\restaurant\dashboard.py --server.port 8502
```

or double-click `run_restaurant_dashboard.bat`. Runs on port 8502 so it can run alongside the
sales dashboard (port 8501).

### Add your own data

Drop a `.csv`/`.xlsx` file into `data_restaurant/`, or use the uploader in the sidebar. The loader
auto-detects common column-name variants, so most Zomato-style exports work without renaming
anything:

| Field | Recognized column names |
|---|---|
| City | `listed_in(city)`, `location`, `city` |
| Country | `country`, `country code`, `listed_in(country)` |
| Cuisines | `cuisines`, `cuisine` (comma-separated, split automatically) |
| Rating | `rate`, `rating`, `aggregate rating` (handles `"4.1/5"`, `"NEW"`, `"-"`) |
| Cost | `approx_cost(for two people)`, `cost`, `price` (handles `"1,200"`) |
| Online order | `online_order`, `has online delivery` (`Yes`/`No`) |
| Table booking | `book_table`, `has table booking` (`Yes`/`No`) |

Any field not found in your file is simply skipped in the relevant chart/insight — it won't crash.
Remove or replace `data_restaurant/sample_restaurants.csv` once you have real data.
