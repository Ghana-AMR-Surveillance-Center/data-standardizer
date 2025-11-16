from __future__ import annotations

import pandas as pd
from typing import Dict
from utils.helpers import standardize_dataframe_columns, strip_object_whitespace
from utils.vocabularies import ORGANISM_SYNONYMS, ANTIBIOTIC_SYNONYMS


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_dataframe_columns(df)
    df = strip_object_whitespace(df)
    return df


def normalize_organism_text(text: str) -> str:
    s = str(text).strip().lower()
    for code, syns in ORGANISM_SYNONYMS.items():
        for syn in syns:
            if syn in s:
                return code
    return ""


def normalize_antibiotic_text(text: str) -> str:
    s = str(text).strip().lower()
    for code, syns in ANTIBIOTIC_SYNONYMS.items():
        for syn in syns:
            if syn in s:
                return code
    up = str(text).strip().upper()
    if 2 <= len(up) <= 4 and up.isalpha():
        return up
    return ""


