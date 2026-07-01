import warnings

import pandas as pd

from src.config import DATA_DIR, SUPPORTED_EXTENSIONS


def _read_file(path):
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_excel(path)


def load_data(data_dir=DATA_DIR):
    """Load and concatenate every supported file in data_dir into one DataFrame."""
    files = sorted(
        p for p in data_dir.glob("*") if p.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not files:
        return pd.DataFrame()

    frames = []
    for path in files:
        df = _read_file(path)
        df["__source_file"] = path.name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True, sort=False)
    return _coerce_types(combined)


def _coerce_types(df):
    for col in df.columns:
        if col == "__source_file":
            continue
        if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                parsed = pd.to_datetime(df[col], errors="coerce")
            if parsed.notna().mean() > 0.8:
                df[col] = parsed
    return df


def detect_date_column(df):
    for col in df.columns:
        if col != "__source_file" and pd.api.types.is_datetime64_any_dtype(df[col]):
            return col
    return None


def detect_numeric_columns(df):
    return [
        col
        for col in df.columns
        if col != "__source_file" and pd.api.types.is_numeric_dtype(df[col])
    ]


def detect_category_columns(df):
    date_col = detect_date_column(df)
    numeric_cols = set(detect_numeric_columns(df))
    return [
        col
        for col in df.columns
        if col != "__source_file"
        and col != date_col
        and col not in numeric_cols
    ]
