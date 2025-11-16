"""
Minimal FastAPI app exposing programmatic endpoints for mapping suggestion,
GLASS validation, and GLASS export. Intended for automation/integration.

Run (dev):
  uvicorn api.app:app --host 0.0.0.0 --port 9000
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Body, HTTPException, Depends, Header
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
import pandas as pd
import os

from core.services.mapping import clean_dataframe
from core.services.interpretation import interpret_nd_nm
from core.services.validation import validate_glass_export
from core.jobs import enqueue, get_job

app = FastAPI(title="AMR Standardizer API", version="1.0.0")

allowed_origins = os.environ.get("CORS_ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in allowed_origins.split(",")] if allowed_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("API_KEY")

def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _similarity(a: str, b: str) -> float:
    try:
        from Levenshtein import ratio as lev_ratio
        return float(lev_ratio(a.lower(), b.lower()))
    except Exception:
        from difflib import SequenceMatcher
        return float(SequenceMatcher(None, a.lower(), b.lower()).ratio())


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/mappings/suggest", dependencies=[Depends(require_api_key)])
def suggest_mappings(headers: List[str] = Body(..., embed=True)) -> Dict[str, Any]:
    # Basic similarity against a canonical list (SchemaAnalyzer.STANDARD_FIELDS if available)
    try:
        from utils.schema_analyzer import SchemaAnalyzer
        targets = SchemaAnalyzer.STANDARD_FIELDS
    except Exception:
        targets = ["Country", "Specimen date", "Specimen type", "Organism", "Age in years", "Gender"]

    suggestions: Dict[str, Dict[str, Any]] = {}
    for t in targets:
        best = None
        best_score = 0.0
        for h in headers:
            s = _similarity(h, t)
            if s > best_score:
                best_score = s
                best = h
        if best and best_score >= 0.6:
            suggestions[t] = {"source": best, "confidence": round(best_score, 3)}

    return {"mappings": suggestions}


@app.post("/v1/validate/glass", dependencies=[Depends(require_api_key)])
def validate_glass(records: List[Dict[str, Any]] = Body(..., embed=True)) -> Dict[str, Any]:
    if not isinstance(records, list):
        raise HTTPException(status_code=400, detail="records must be a list of objects")
    df = pd.DataFrame.from_records(records)
    res = validate_glass_export(df)
    return res


@app.post("/v1/export/glass/csv", dependencies=[Depends(require_api_key)])
def export_glass_csv(records: List[Dict[str, Any]] = Body(..., embed=True)) -> StreamingResponse:
    df = pd.DataFrame.from_records(records)
    try:
        from utils.glass_exporter import build_glass_export
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"exporter not available: {str(ex)}")
    df = clean_dataframe(df)
    g = build_glass_export(df)
    buf = io.BytesIO(g.to_csv(index=False).encode("utf-8"))
    return StreamingResponse(buf, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=glass.csv"})


@app.post("/v1/interpret/ndnm", dependencies=[Depends(require_api_key)])
def api_interpret_ndnm(records: List[Dict[str, Any]] = Body(..., embed=True)) -> Dict[str, Any]:
    if not isinstance(records, list):
        raise HTTPException(status_code=400, detail="records must be a list of objects")
    df = pd.DataFrame.from_records(records)
    df = clean_dataframe(df)
    out = interpret_nd_nm(df)
    return {"columns": out.columns.tolist(), "rows": out.to_dict(orient="records")}


@app.post("/v1/jobs/interpret-ndnm", dependencies=[Depends(require_api_key)])
def api_jobs_interpret_ndnm(records: List[Dict[str, Any]] = Body(..., embed=True)) -> Dict[str, Any]:
    if not isinstance(records, list):
        raise HTTPException(status_code=400, detail="records must be a list of objects")
    job_id = enqueue("core.tasks.task_interpret_ndnm", records)
    return {"job_id": job_id}


@app.post("/v1/jobs/export-glass", dependencies=[Depends(require_api_key)])
def api_jobs_export_glass(records: List[Dict[str, Any]] = Body(..., embed=True)) -> Dict[str, Any]:
    if not isinstance(records, list):
        raise HTTPException(status_code=400, detail="records must be a list of objects")
    # Pass job_id at runtime; worker will save artifact with job_id in filename
    job_id = enqueue("core.tasks.task_export_glass", records, job_id="__rq_job_id__")
    return {"job_id": job_id}


@app.get("/v1/jobs/{job_id}", dependencies=[Depends(require_api_key)])
def api_job_status(job_id: str) -> Dict[str, Any]:
    return get_job(job_id)


