from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"

# How often the dashboard re-reads DATA_DIR and reruns, in seconds.
AUTO_REFRESH_SECONDS = 60

SUPPORTED_EXTENSIONS = (".csv", ".xlsx", ".xls")
