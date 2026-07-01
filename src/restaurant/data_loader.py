import re

import pandas as pd

from src.restaurant.config import COLUMN_ALIASES, DATA_DIR, SUPPORTED_EXTENSIONS


def _read_file(path):
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_excel(path)


def _map_columns(df):
    """Rename whichever alias columns are present to their canonical field name."""
    lower_lookup = {col.strip().lower(): col for col in df.columns}
    rename_map = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            match = lower_lookup.get(alias.lower())
            if match:
                rename_map[match] = canonical
                break
    return df.rename(columns=rename_map)


def _parse_rating(series):
    cleaned = series.astype(str).str.extract(r"(\d+(?:\.\d+)?)")[0]
    return pd.to_numeric(cleaned, errors="coerce")


def _parse_cost(series):
    cleaned = series.astype(str).str.replace(",", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def _parse_yes_no(series):
    normalized = series.astype(str).str.strip().str.lower()
    return normalized.map({"yes": True, "no": False})


def _coerce_types(df):
    if "rating" in df.columns:
        df["rating"] = _parse_rating(df["rating"])
    if "cost" in df.columns:
        df["cost"] = _parse_cost(df["cost"])
    if "online_order" in df.columns:
        df["online_order"] = _parse_yes_no(df["online_order"])
    if "book_table" in df.columns:
        df["book_table"] = _parse_yes_no(df["book_table"])
    if "cuisines" in df.columns:
        df["cuisines"] = df["cuisines"].astype(str).str.strip()
    return df


def load_data(data_dir=DATA_DIR):
    """Load and concatenate every supported file in data_dir, mapped to canonical columns."""
    files = sorted(
        p for p in data_dir.glob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not files:
        return pd.DataFrame()

    frames = []
    for path in files:
        df = _map_columns(_read_file(path))
        df["__source_file"] = path.name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True, sort=False)
    return _coerce_types(combined)


def available_fields(df):
    """Which canonical fields (city, country, cuisines, rating, cost, online_order,
    book_table) are actually present and usable in this dataset."""
    canonical_fields = list(COLUMN_ALIASES.keys())
    return [f for f in canonical_fields if f in df.columns and df[f].notna().any()]
