"""
WHONET-like CSV exporter (simplified).
Produces a wide table with organism code and antibiotic columns as SIR.
"""

from __future__ import annotations

from typing import List, Dict
import pandas as pd


def build_whonet_wide(df: pd.DataFrame, organism_col: str = "ORGANISM") -> pd.DataFrame:
    """
    Accepts a GLASS-long dataframe (COUNTRY,SPECIMENDATE,SPECIMEN,ORGANISM,ANTIBIOTIC,INTERPRETATION,...)
    and pivots to wide: one row per (COUNTRY,SPECIMENDATE,SPECIMEN,ORGANISM),
    columns per ANTIBIOTIC with S/I/R values.
    """
    required = {"COUNTRY", "SPECIMENDATE", "SPECIMEN", "ORGANISM", "ANTIBIOTIC", "INTERPRETATION"}
    if not required.issubset(set(df.columns)):
        return pd.DataFrame()

    base_cols = ["COUNTRY", "SPECIMENDATE", "SPECIMEN", "ORGANISM"]
    pivot = df.pivot_table(
        index=base_cols,
        columns="ANTIBIOTIC",
        values="INTERPRETATION",
        aggfunc=lambda x: x.iloc[0],
    ).reset_index()

    # Flatten columns
    pivot.columns = [str(c) for c in pivot.columns]
    return pivot


