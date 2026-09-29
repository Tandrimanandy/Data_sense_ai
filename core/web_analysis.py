"""
DataSense AI - Web Analysis Helpers
Reusable data loading and profiling functions for the Flask backend.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def load_dataframe(file_storage) -> pd.DataFrame:
    """Load an uploaded CSV or Excel file into a DataFrame."""
    filename = file_storage.filename or ""
    extension = _get_extension(filename)

    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Unsupported file type. Please upload one of: {allowed}")

    if extension == ".csv":
        return _read_csv(file_storage)

    return pd.read_excel(file_storage, sheet_name=0)


def analyze_dataframe(df: pd.DataFrame, filename: str = "") -> Dict[str, Any]:
    """Return a compact, JSON-safe analysis profile for a DataFrame."""
    if df.empty:
        raise ValueError("The uploaded file does not contain any rows.")

    row_count = int(len(df))
    column_count = int(len(df.columns))
    numeric_columns = list(df.select_dtypes(include=[np.number]).columns)
    categorical_columns = [col for col in df.columns if col not in numeric_columns]

    columns = [_analyze_column(df, col, row_count) for col in df.columns]
    total_nan = int(df.isna().sum().sum())
    total_numeric_zeros = int((df[numeric_columns] == 0).sum().sum()) if numeric_columns else 0
    total_zero_like = sum(column["zero_like_count"] for column in columns)

    numeric_stats = _numeric_statistics(df[numeric_columns]) if numeric_columns else {}
    correlations = _strong_correlations(df[numeric_columns]) if len(numeric_columns) > 1 else []

    result = {
        "filename": filename,
        "summary": {
            "rows": row_count,
            "columns": column_count,
            "numeric_columns": len(numeric_columns),
            "categorical_columns": len(categorical_columns),
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_mb": round(float(df.memory_usage(deep=True).sum() / (1024 * 1024)), 4),
            "total_nan": total_nan,
            "total_nan_percent": _percent(total_nan, row_count * column_count),
            "total_numeric_zeros": total_numeric_zeros,
            "total_zero_like_values": int(total_zero_like),
        },
        "columns": columns,
        "numeric_statistics": numeric_stats,
        "strong_correlations": correlations,
        "preview": _preview_rows(df),
    }
    result["insights"] = _build_insights(result)
    return _json_safe(result)


def apply_chat_instruction(analysis: Dict[str, Any], instruction: str = "") -> Dict[str, Any]:
    """Focus the analysis output based on a simple local chat instruction."""
    focused = dict(analysis)
    instruction = (instruction or "").strip()
    text = instruction.lower()

    visible_sections = {
        "summary": True,
        "insights": True,
        "columns": True,
        "numeric_statistics": True,
        "strong_correlations": True,
        "preview": True,
    }

    if not text:
        focused["chat"] = {
            "instruction": "",
            "response": "Showing the full analysis.",
            "visible_sections": visible_sections,
        }
        return focused

    response_parts: List[str] = []
    focused_section = "full"

    if _mentions_any(text, ["nan", "null", "missing", "blank", "empty"]):
        focused_section = "columns"
        focused["columns"] = [
            column for column in analysis["columns"] if column.get("nan_count", 0) > 0
        ]
        visible_sections.update(
            {
                "numeric_statistics": False,
                "strong_correlations": False,
                "preview": False,
            }
        )
        response_parts.append("Showing only columns that contain NaN, null, blank, or missing values.")

    elif _mentions_any(text, ["zero", "zeros", "0 values", "0 value"]):
        focused_section = "columns"
        focused["columns"] = [
            column
            for column in analysis["columns"]
            if column.get("zero_count", 0) > 0 or column.get("zero_like_count", 0) > 0
        ]
        visible_sections.update(
            {
                "numeric_statistics": False,
                "strong_correlations": False,
                "preview": False,
            }
        )
        response_parts.append("Showing only columns that contain numeric zeros or zero-like text values.")

    elif _mentions_any(text, ["correlation", "correlations", "relationship", "relationships"]):
        focused_section = "strong_correlations"
        visible_sections.update(
            {
                "columns": False,
                "numeric_statistics": False,
                "preview": False,
            }
        )
        response_parts.append("Showing only strong numeric correlations.")

    elif _mentions_any(text, ["numeric", "statistics", "stats", "mean", "median", "average"]):
        focused_section = "numeric_statistics"
        visible_sections.update(
            {
                "columns": False,
                "strong_correlations": False,
                "preview": False,
            }
        )
        response_parts.append("Showing only numeric statistics.")

    elif _mentions_any(text, ["preview", "sample", "rows", "records", "data"]):
        focused_section = "preview"
        visible_sections.update(
            {
                "columns": False,
                "numeric_statistics": False,
                "strong_correlations": False,
            }
        )
        response_parts.append("Showing only the data preview.")

    elif _mentions_any(text, ["summary", "overview", "total", "totals"]):
        focused_section = "summary"
        visible_sections.update(
            {
                "columns": False,
                "numeric_statistics": False,
                "strong_correlations": False,
                "preview": False,
            }
        )
        response_parts.append("Showing only the summary and key insights.")

    else:
        response_parts.append(
            "I could not match a specific filter, so I am showing the full analysis."
        )

    limit = _extract_limit(text)
    if limit:
        if focused_section == "preview":
            focused["preview"] = analysis.get("preview", [])[:limit]
        elif focused_section == "columns":
            focused["columns"] = focused.get("columns", [])[:limit]
        elif focused_section == "strong_correlations":
            focused["strong_correlations"] = analysis.get("strong_correlations", [])[:limit]
        elif focused_section == "numeric_statistics":
            focused["numeric_statistics"] = dict(
                list(analysis.get("numeric_statistics", {}).items())[:limit]
            )
        else:
            focused["preview"] = analysis.get("preview", [])[:limit]
            focused["columns"] = focused.get("columns", [])[:limit]
            focused["strong_correlations"] = analysis.get("strong_correlations", [])[:limit]
            focused["numeric_statistics"] = dict(
                list(analysis.get("numeric_statistics", {}).items())[:limit]
            )
        response_parts.append(f"Limited visible lists to {limit} item(s).")

    if not focused.get("columns") and visible_sections["columns"]:
        response_parts.append("No matching columns were found for that instruction.")

    focused["chat"] = {
        "instruction": instruction,
        "response": " ".join(response_parts),
        "visible_sections": visible_sections,
    }
    return _json_safe(focused)


def _read_csv(file_storage) -> pd.DataFrame:
    """Read CSV uploads with a few common encodings."""
    encodings = ("utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1")
    last_error: Optional[Exception] = None

    for encoding in encodings:
        try:
            file_storage.stream.seek(0)
            return pd.read_csv(file_storage.stream, encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc

    raise ValueError("Could not decode the CSV file with common encodings.") from last_error


def _mentions_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _extract_limit(text: str) -> Optional[int]:
    patterns = (
        r"\b(?:first|top|only|show|limit)\s+(\d+)\b",
        r"\b(\d+)\s+(?:rows|records|columns|items|results)\b",
    )

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return max(1, min(int(match.group(1)), 100))

    return None


def _analyze_column(df: pd.DataFrame, column: str, row_count: int) -> Dict[str, Any]:
    series = df[column]
    nan_count = int(series.isna().sum())
    zero_count = 0

    if pd.api.types.is_numeric_dtype(series):
        zero_count = int((series == 0).sum())

    zero_like_count = int(series.astype("string").str.strip().isin(["0", "0.0"]).sum())

    column_result = {
        "name": str(column),
        "dtype": str(series.dtype),
        "nan_count": nan_count,
        "nan_percent": _percent(nan_count, row_count),
        "zero_count": zero_count,
        "zero_percent": _percent(zero_count, row_count),
        "zero_like_count": zero_like_count,
        "unique_count": int(series.nunique(dropna=True)),
        "non_null_count": int(series.notna().sum()),
    }

    if pd.api.types.is_numeric_dtype(series):
        clean = series.dropna()
        if not clean.empty:
            column_result.update(
                {
                    "mean": float(clean.mean()),
                    "median": float(clean.median()),
                    "std": float(clean.std()) if len(clean) > 1 else 0.0,
                    "min": float(clean.min()),
                    "max": float(clean.max()),
                    "q25": float(clean.quantile(0.25)),
                    "q75": float(clean.quantile(0.75)),
                }
            )
    else:
        top_values = series.dropna().astype(str).value_counts().head(5).to_dict()
        column_result["top_values"] = top_values

    return column_result


def _numeric_statistics(numeric_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    stats: Dict[str, Dict[str, Any]] = {}

    for column in numeric_df.columns:
        clean = numeric_df[column].dropna()
        if clean.empty:
            continue

        stats[str(column)] = {
            "mean": float(clean.mean()),
            "median": float(clean.median()),
            "std": float(clean.std()) if len(clean) > 1 else 0.0,
            "min": float(clean.min()),
            "max": float(clean.max()),
            "zeros": int((clean == 0).sum()),
            "negative_values": int((clean < 0).sum()),
            "positive_values": int((clean > 0).sum()),
        }

    return stats


def _strong_correlations(numeric_df: pd.DataFrame) -> List[Dict[str, Any]]:
    corr = numeric_df.corr(numeric_only=True)
    correlations: List[Dict[str, Any]] = []

    for index, col_a in enumerate(corr.columns):
        for col_b in corr.columns[index + 1 :]:
            value = corr.loc[col_a, col_b]
            if pd.notna(value) and abs(value) >= 0.5:
                correlations.append(
                    {
                        "column_a": str(col_a),
                        "column_b": str(col_b),
                        "correlation": round(float(value), 4),
                    }
                )

    return sorted(correlations, key=lambda item: abs(item["correlation"]), reverse=True)


def _preview_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    preview = df.head(10).replace({np.nan: None})
    return preview.to_dict(orient="records")


def _build_insights(result: Dict[str, Any]) -> List[str]:
    summary = result["summary"]
    columns = result["columns"]
    insights: List[str] = []

    insights.append(
        f"Loaded {summary['rows']} rows and {summary['columns']} columns from the uploaded file."
    )

    if summary["total_nan"]:
        worst_nan = max(columns, key=lambda column: column["nan_count"])
        insights.append(
            f"Missing values found: {summary['total_nan']} NaN/blank cells. "
            f"The highest missing count is in '{worst_nan['name']}' with {worst_nan['nan_count']} cells."
        )
    else:
        insights.append("No NaN/blank values were detected.")

    if summary["total_numeric_zeros"]:
        worst_zero = max(columns, key=lambda column: column["zero_count"])
        insights.append(
            f"Numeric zeros found: {summary['total_numeric_zeros']} cells. "
            f"'{worst_zero['name']}' contains the most numeric zeros."
        )
    else:
        insights.append("No numeric zero values were detected.")

    if summary["duplicate_rows"]:
        insights.append(f"{summary['duplicate_rows']} duplicate rows were detected.")

    if result["strong_correlations"]:
        top_corr = result["strong_correlations"][0]
        insights.append(
            f"Strongest numeric correlation: '{top_corr['column_a']}' and "
            f"'{top_corr['column_b']}' ({top_corr['correlation']})."
        )

    return insights


def _get_extension(filename: str) -> str:
    dot_index = filename.rfind(".")
    return filename[dot_index:].lower() if dot_index != -1 else ""


def _percent(part: int, whole: int) -> float:
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)


def _json_safe(value: Any) -> Any:
    """Convert pandas/numpy values and NaN-like values into JSON-safe Python values."""
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if pd.isna(value) and not isinstance(value, (str, bytes)):
        return None
    return value
