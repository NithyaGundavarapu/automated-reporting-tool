from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data_restaurant"

AUTO_REFRESH_SECONDS = 60
SUPPORTED_EXTENSIONS = (".csv", ".xlsx", ".xls")

# Default alert thresholds, editable in the dashboard sidebar.
DEFAULT_MIN_AVG_RATING = 3.5
DEFAULT_MIN_ONLINE_ORDER_PCT = 50.0
DEFAULT_MIN_BOOK_TABLE_PCT = 20.0

# Column name aliases -> canonical field name.
COLUMN_ALIASES = {
    "name": ["name", "restaurant name", "restaurant"],
    "city": ["listed_in(city)", "location", "city"],
    "country": ["country", "country code", "listed_in(country)"],
    "cuisines": ["cuisines", "cuisine"],
    "rating": ["rate", "rating", "aggregate rating"],
    "cost": ["approx_cost(for two people)", "approx_cost", "cost", "price", "average cost for two"],
    "online_order": ["online_order", "has online delivery", "online delivery"],
    "book_table": ["book_table", "has table booking", "table booking"],
    "votes": ["votes"],
}
