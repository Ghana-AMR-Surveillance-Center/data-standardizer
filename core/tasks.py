from __future__ import annotations

import os
import pandas as pd
from typing import Dict, Any, List
from core.services.mapping import clean_dataframe
from core.services.interpretation import interpret_nd_nm
from core.services.validation import validate_glass_export
from core.services.audit import log_event
from utils.glass_exporter import build_glass_export


def task_interpret_ndnm(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    df = pd.DataFrame.from_records(records)
    df = clean_dataframe(df)
    out = interpret_nd_nm(df)
    log_event("job.interpret_ndnm.completed", {"rows": len(out)})
    return {"columns": out.columns.tolist(), "rows": out.to_dict(orient="records")}


def task_export_glass(records: List[Dict[str, Any]], job_id: str) -> Dict[str, Any]:
    df = pd.DataFrame.from_records(records)
    df = clean_dataframe(df)
    g = build_glass_export(df)
    os.makedirs("artifacts", exist_ok=True)
    out_path = os.path.join("artifacts", f"glass_{job_id}.csv")
    g.to_csv(out_path, index=False)
    val = validate_glass_export(g)
    log_event("job.export_glass.completed", {"rows": len(g), "file": out_path, "validation": val.get("summary", {})})
    return {"file": out_path, "validation": val}


