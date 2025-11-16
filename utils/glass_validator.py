"""
WHO GLASS Validator
Validates a GLASS-long dataframe produced by glass_exporter.build_glass_export().
Checks required fields, formats, and simple semantic constraints.
"""

from __future__ import annotations

from typing import Dict, Any, List
import pandas as pd
import re
from .vocabularies import SPECIMEN_CODES
import datetime as _dt

REQUIRED_COLUMNS = [
    "COUNTRY",
    "SPECIMENDATE",
    "SPECIMEN",
    "ORGANISM",
    "ANTIBIOTIC",
    "INTERPRETATION",
]


def validate_glass_df(df: pd.DataFrame) -> Dict[str, Any]:
    results: Dict[str, Any] = {
        "summary": {"total": len(df), "errors": 0, "warnings": 0},
        "errors": [],
        "warnings": [],
        "checks": {},
    }

    # Column presence
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        results["errors"].append({"type": "missing_columns", "columns": missing_cols})
        results["summary"]["errors"] += 1
        # Early exit if structurally invalid
        return results

    # Country format (2-letter)
    invalid_country = ~df["COUNTRY"].astype(str).str.match(r"^[A-Z]{2}$")
    if invalid_country.any():
        idxs = df.index[invalid_country].tolist()
        results["errors"].append({"type": "invalid_country", "rows": idxs})
        results["summary"]["errors"] += 1

    # Date format (YYYY-MM-DD) and not in future (best-effort)
    date_parsed = pd.to_datetime(df["SPECIMENDATE"], errors="coerce")
    invalid_date = date_parsed.isna()
    if invalid_date.any():
        idxs = df.index[invalid_date].tolist()
        results["errors"].append({"type": "invalid_specimen_date", "rows": idxs})
        results["summary"]["errors"] += 1
    else:
        today = _dt.date.today()
        future = date_parsed.dt.date > today
        if future.any():
            results["errors"].append({"type": "future_specimen_date", "rows": df.index[future].tolist()})
            results["summary"]["errors"] += 1

    # INTERPRETATION in S/I/R
    valid_interp = df["INTERPRETATION"].isin(["S", "I", "R"])
    bad_interp = ~valid_interp
    if bad_interp.any():
        idxs = df.index[bad_interp].tolist()
        results["errors"].append({"type": "invalid_interpretation", "rows": idxs})
        results["summary"]["errors"] += 1

    # SPECIMEN code set
    if "SPECIMEN" in df.columns:
        bad_spec = ~df["SPECIMEN"].isin(SPECIMEN_CODES)
        if bad_spec.any():
            results["warnings"].append({"type": "unknown_specimen_code", "rows": df.index[bad_spec].tolist()})
            results["summary"]["warnings"] += 1

    # ORGANISM/ANTIBIOTIC patterns
    if "ORGANISM" in df.columns:
        bad_org = ~df["ORGANISM"].astype(str).str.match(r"^[A-Z]{2,4}$")
        if bad_org.any():
            results["warnings"].append({"type": "organism_code_pattern", "rows": df.index[bad_org].tolist()})
            results["summary"]["warnings"] += 1

    if "ANTIBIOTIC" in df.columns:
        bad_ab = ~df["ANTIBIOTIC"].astype(str).str.match(r"^[A-Z]{2,4}$")
        if bad_ab.any():
            results["warnings"].append({"type": "antibiotic_code_pattern", "rows": df.index[bad_ab].tolist()})
            results["summary"]["warnings"] += 1

    # PATIENT_TYPE allowed values if present
    if "PATIENT_TYPE" in df.columns:
        bad_pt = ~df["PATIENT_TYPE"].isin(["IN", "OUT", "UNK"])
        if bad_pt.any():
            results["warnings"].append({"type": "patient_type_value", "rows": df.index[bad_pt].tolist()})
            results["summary"]["warnings"] += 1

    # Optional fields checks
    if "AGE" in df.columns:
        # Age should be 0..120 when provided
        def _age_bad(x):
            try:
                if pd.isna(x) or x == "":
                    return False
                v = int(x)
                return not (0 <= v <= 120)
            except Exception:
                return True

        bad_age = df["AGE"].apply(_age_bad)
        if bad_age.any():
            results["warnings"].append({"type": "age_out_of_range", "rows": df.index[bad_age].tolist()})
            results["summary"]["warnings"] += 1

    if "SEX" in df.columns:
        bad_sex = ~df["SEX"].isin(["M", "F", "U"])
        if bad_sex.any():
            results["warnings"].append({"type": "invalid_sex", "rows": df.index[bad_sex].tolist()})
            results["summary"]["warnings"] += 1

    # Pass/Fail
    results["summary"]["passed"] = results["summary"]["errors"] == 0
    return results


