from __future__ import annotations

import pandas as pd
from typing import Dict, Any
from utils.glass_validator import validate_glass_df


def validate_glass_export(df: pd.DataFrame) -> Dict[str, Any]:
    return validate_glass_df(df)


