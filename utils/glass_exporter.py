"""
WHO GLASS Exporter
Transforms a wide AMR dataframe (with SIR or *_INTERPRETATION columns) into
WHO GLASS-ready long-format CSV/JSON with strict column order.

Assumptions:
- Input dataframe contains at least: Country, Specimen date, Specimen type, Organism,
  optional: Age in years, Gender, Department/Ward, Location type (for inpatient/outpatient).
- AST results appear as either:
  - Columns ending with 'SIR' holding values in {'S','I','R'} (e.g., CiprofloxacinSIR)
  - Columns ending with '_INTERPRETATION' (e.g., CIP_INTERPRETATION)

This module provides best-effort normalization suitable for non-technical operators
while logging conservative fallbacks for unknowns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import re
from .vocabularies import ORGANISM_SYNONYMS, ANTIBIOTIC_SYNONYMS, SPECIMEN_CODES


# Exact output order for WHO GLASS (example baseline; adjust per country template if needed)
GLASS_COLUMNS: List[str] = [
    "COUNTRY",
    "SPECIMENDATE",
    "SPECIMEN",
    "ORGANISM",
    "ANTIBIOTIC",
    "INTERPRETATION",
    "AGE",
    "SEX",
    "PATIENT_TYPE",
    "WARD",
]


# Minimal mapping dictionaries (extendable)
def _organism_to_code(name: str) -> Optional[str]:
    s = re.sub(r"\s+", " ", name.strip().lower())
    for code, synonyms in ORGANISM_SYNONYMS.items():
        for syn in synonyms:
            if syn in s:
                return code
    return None


def _antibiotic_to_code(token: str) -> Optional[str]:
    s = token.strip().lower().replace("_", " ").replace("-", " ")
    # Try synonyms
    for code, synonyms in ANTIBIOTIC_SYNONYMS.items():
        for syn in synonyms:
            if syn in s:
                return code
    # Short code guess
    upper = token.strip().upper()
    if 2 <= len(upper) <= 4 and upper.isalpha():
        return upper
    return None


@dataclass
class GlassMappingConfig:
    country_col: str = "Country"
    specimen_date_col: str = "Specimen date"
    specimen_type_col: str = "Specimen type"
    organism_col: str = "Organism"
    age_col: str = "Age in years"
    sex_col: str = "Gender"
    ward_col: str = "Department"
    patient_type_col: str = "Location type"


def _first_existing_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    # Case and whitespace insensitive match
    norm_map = {str(c).strip().lower(): c for c in df.columns}
    for c in candidates:
        key = str(c).strip().lower()
        if key in norm_map:
            return norm_map[key]
    # Fallback: try direct containment ignoring multiple spaces
    for c in candidates:
        target = " ".join(str(c).strip().lower().split())
        for k, v in norm_map.items():
            if " ".join(k.split()) == target:
                return v
    return None


def _normalize_sex(value: object) -> str:
    if pd.isna(value):
        return "U"
    s = str(value).strip().upper()
    if s in {"M", "MALE"}:
        return "M"
    if s in {"F", "FEMALE"}:
        return "F"
    return "U"


def _normalize_patient_type(value: object) -> str:
    if pd.isna(value):
        return "UNK"
    s = str(value).strip().lower()
    if s.startswith("in"):
        return "IN"
    if s.startswith("out"):
        return "OUT"
    return "UNK"


def _normalize_specimen(value: object) -> str:
    if pd.isna(value):
        return "UNK"
    s = str(value).strip().lower()
    # heuristic mapping
    if "blood" in s:
        return "BL"
    if "urine" in s:
        return "UR"
    if "sputum" in s:
        return "SP"
    if "csf" in s or "cerebrospinal" in s:
        return "CSF"
    if "stool" in s or "feces" in s:
        return "ST"
    return "UNK"


def _normalize_organism(value: object) -> Tuple[str, float]:
    if pd.isna(value):
        return ("XXX", 0.0)
    s = str(value).strip().lower()
    code = _organism_to_code(s)
    if code:
        return (code, 0.9)
    # crude fallback
    simple = re.sub(r"[^a-z]", "", s)
    for c, syns in ORGANISM_SYNONYMS.items():
        for syn in syns:
            if re.sub(r"[^a-z]", "", syn) in simple:
                return (c, 0.8)
    return ("XXX", 0.0)


def _antibiotic_from_header(col: str) -> Optional[str]:
    name = col.replace("_INTERPRETATION", "").replace("SIR", "").strip()
    code = _antibiotic_to_code(name)
    return code


def build_glass_export(df: pd.DataFrame, cfg: Optional[GlassMappingConfig] = None) -> pd.DataFrame:
    """
    Transform the provided dataframe into WHO GLASS long format.
    Returns a DataFrame with GLASS_COLUMNS in exact order.
    """
    cfg = cfg or GlassMappingConfig()
    df_local = df.copy()

    # Column candidates for resilience
    c_country = _first_existing_col(df_local, [cfg.country_col, "COUNTRY", "country"])
    c_date = _first_existing_col(df_local, [cfg.specimen_date_col, "Specimen Date", "SPECIMENDATE", "specimen_date"])
    c_specimen = _first_existing_col(df_local, [cfg.specimen_type_col, "Specimen", "SPECIMEN", "specimen"])
    c_org = _first_existing_col(df_local, [cfg.organism_col, "ORGANISM", "organism"])
    c_age = _first_existing_col(df_local, [cfg.age_col, "AGE", "Age"])
    c_sex = _first_existing_col(df_local, [cfg.sex_col, "SEX", "Sex"])
    c_ward = _first_existing_col(df_local, [cfg.ward_col, "WARD", "Ward", "Department"])
    c_ptype = _first_existing_col(df_local, [cfg.patient_type_col, "PATIENT_TYPE", "PatientType", "Location type"])

    # Prepare base columns
    country_vals = df_local[c_country] if c_country else pd.Series([""] * len(df_local))
    date_vals = pd.to_datetime(df_local[c_date], errors="coerce").dt.date if c_date else pd.Series([pd.NaT] * len(df_local))
    specimen_vals = df_local[c_specimen] if c_specimen else pd.Series([""] * len(df_local))
    org_vals = df_local[c_org] if c_org else pd.Series([""] * len(df_local))
    age_vals = pd.to_numeric(df_local[c_age], errors="coerce").round().astype("Int64") if c_age else pd.Series([pd.NA] * len(df_local), dtype="Int64")
    sex_vals = df_local[c_sex] if c_sex else pd.Series(["U"] * len(df_local))
    ward_vals = df_local[c_ward] if c_ward else pd.Series([""] * len(df_local))
    ptype_vals = df_local[c_ptype] if c_ptype else pd.Series(["UNK"] * len(df_local))

    # Identify AST interpretation columns
    sir_cols = [c for c in df_local.columns if c.endswith("SIR")]
    interp_cols = [c for c in df_local.columns if c.endswith("_INTERPRETATION")]
    ast_cols = sir_cols + interp_cols

    records: List[Dict[str, object]] = []
    for idx in df_local.index:
        org_code, _ = _normalize_organism(org_vals.iloc[idx] if len(org_vals) > 0 else pd.NA)
        spec_code = _normalize_specimen(specimen_vals.iloc[idx] if len(specimen_vals) > 0 else pd.NA)
        sex_norm = _normalize_sex(sex_vals.iloc[idx] if len(sex_vals) > 0 else pd.NA)
        ptype_norm = _normalize_patient_type(ptype_vals.iloc[idx] if len(ptype_vals) > 0 else pd.NA)

        for col in ast_cols:
            antibiotic = _antibiotic_from_header(col)
            if not antibiotic:
                continue
            raw_val = df_local.at[idx, col]
            if pd.isna(raw_val):
                continue
            val = str(raw_val).strip().upper()
            if val not in {"S", "I", "R"}:
                # attempt normalization of common words
                if val in {"SUSCEPTIBLE", "SENSITIVE"}:
                    val = "S"
                elif val in {"INTERMEDIATE"}:
                    val = "I"
                elif val in {"RESISTANT"}:
                    val = "R"
                else:
                    continue

            rec = {
                "COUNTRY": (country_vals.iloc[idx] if len(country_vals) > 0 else ""),
                "SPECIMENDATE": (str(date_vals.iloc[idx]) if len(date_vals) > 0 and pd.notna(date_vals.iloc[idx]) else ""),
                "SPECIMEN": spec_code,
                "ORGANISM": org_code,
                "ANTIBIOTIC": antibiotic,
                "INTERPRETATION": val,
                "AGE": (int(age_vals.iloc[idx]) if len(age_vals) > 0 and pd.notna(age_vals.iloc[idx]) else ""),
                "SEX": sex_norm,
                "PATIENT_TYPE": ptype_norm,
                "WARD": (ward_vals.iloc[idx] if len(ward_vals) > 0 else ""),
            }
            records.append(rec)

    out = pd.DataFrame.from_records(records, columns=GLASS_COLUMNS)
    return out


def to_glass_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def to_glass_json_bytes(df: pd.DataFrame) -> bytes:
    return df.to_json(orient="records", indent=2).encode("utf-8")


