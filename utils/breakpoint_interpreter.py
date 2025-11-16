"""
Breakpoint interpreter that converts MIC/zone values to S/I/R
using a versioned registry (CLSI/EUCAST).
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
from .breakpoints import registry_get


def interpret_value(
    organism_code: str,
    antibiotic_code: str,
    method: str,
    value: float,
    comparator: str | None,
    standard: str,
    version: str,
) -> str:
    bp = registry_get(standard, version, organism_code, antibiotic_code, method)
    if not bp:
        return "No Breakpoints"

    if method == "mic":
        # normalize comparator: ≤ v is treated as v
        v = float(value)
        s_le = bp.get("mic_s_le")
        i_le = bp.get("mic_i_le")
        if s_le is None or i_le is None:
            return "No Breakpoints"
        if v <= s_le:
            return "S"
        if v <= i_le:
            return "I"
        return "R"

    # zone
    z = float(value)
    s_ge = bp.get("zone_s_ge")
    i_ge = bp.get("zone_i_ge")
    if s_ge is None or i_ge is None:
        return "No Breakpoints"
    if z >= s_ge:
        return "S"
    if z >= i_ge:
        return "I"
    return "R"


def apply_interpretation_to_dataframe(
    df: pd.DataFrame,
    organism_col: str,
    method_cols: dict,
    standard: str = "CLSI",
    version: str = "2024",
) -> pd.DataFrame:
    """
    Given a dataframe and mapping of method to columns, create *_INTERPRETATION columns.
    method_cols example:
      {
        "zone": ["CIP_ND","CAZ_ND"],
        "mic": ["CIP_NM"]
      }
    Antimicrobial code is derived from column names: CIP_ND -> CIP.
    """
    out = df.copy()
    for method, cols in method_cols.items():
        for col in cols:
            if col not in out.columns:
                continue
            if method == "zone":
                am_code = col.split("_ND")[0].upper()
            elif method == "mic":
                am_code = col.split("_NM")[0].upper()
            else:
                continue

            new_col = f"{am_code}_INTERPRETATION"
            out[new_col] = "Not Tested"
            for idx, row in out.iterrows():
                org_code = str(row.get(organism_col, "")).upper()
                val = row[col]
                if pd.isna(val) or val == "":
                    continue
                try:
                    v = float(val)
                except Exception:
                    continue
                interp = interpret_value(org_code, am_code, method, v, None, standard, version)
                if interp in {"S", "I", "R"}:
                    out.at[idx, new_col] = interp
    return out


