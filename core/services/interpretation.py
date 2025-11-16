from __future__ import annotations

import pandas as pd
from typing import Dict, List
from utils.breakpoint_interpreter import apply_interpretation_to_dataframe


def interpret_nd_nm(
    df: pd.DataFrame,
    organism_col: str = "Organism",
    standard: str = "CLSI",
    version: str = "2024",
) -> pd.DataFrame:
    zone_cols = [c for c in df.columns if c.endswith("_ND")]
    mic_cols = [c for c in df.columns if c.endswith("_NM")]
    if not zone_cols and not mic_cols:
        return df
    return apply_interpretation_to_dataframe(
        df,
        organism_col=organism_col,
        method_cols={"zone": zone_cols, "mic": mic_cols},
        standard=standard,
        version=version,
    )


