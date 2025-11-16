"""
HL7 v2 (simplified) Importer
Parses pipe-delimited HL7 v2 messages (string) to a DataFrame.
Focus on PID, OBR, OBX segments for minimal AMR content extraction.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
from ..vocabularies import ANTIBIOTIC_SYNONYMS


def _field(seg: str, idx: int) -> str:
    parts = seg.split("|")
    return parts[idx] if len(parts) > idx else ""


def _antibiotic_from_obx3(obx3: str) -> Optional[str]:
    # OBX-3 like "CIP^Ciprofloxacin^LN"
    tokens = obx3.split("^")
    candidates = [t for t in tokens if t]
    if not candidates:
        return None
    text = candidates[1] if len(candidates) > 1 else candidates[0]
    s = text.strip().lower()
    for code, syns in ANTIBIOTIC_SYNONYMS.items():
        for syn in syns:
            if syn in s:
                return code
    up = text.strip().upper()
    if 2 <= len(up) <= 4 and up.isalpha():
        return up
    return None


def import_hl7_message(message: str) -> pd.DataFrame:
    lines = [ln for ln in message.replace("\r\n", "\n").split("\n") if ln.strip()]
    patient_gender = ""
    patient_age = ""
    specimen_date = ""
    specimen_type = ""

    rows: List[Dict[str, Any]] = []
    for ln in lines:
        if ln.startswith("PID|"):
            # PID-8 gender
            patient_gender = _field(ln, 8)
        elif ln.startswith("OBR|"):
            # OBR-7 observation date/time; OBR-15 specimen source
            dt = _field(ln, 7)
            try:
                if dt:
                    # YYYYMMDDHHMM or YYYYMMDD
                    if len(dt) >= 8:
                        specimen_date = datetime.strptime(dt[:8], "%Y%m%d").date().isoformat()
            except Exception:
                pass
            specimen_type = _field(ln, 15)
        elif ln.startswith("OBX|"):
            # OBX-3 test code/name; OBX-5 value (S/I/R)
            obx3 = _field(ln, 3)
            ab = _antibiotic_from_obx3(obx3)
            val = _field(ln, 5).strip()
            if ab and val:
                rec = {
                    "Organism": "",
                    "Specimen date": specimen_date or "",
                    "Specimen type": specimen_type or "",
                    "Gender": patient_gender or "",
                    "Age in years": patient_age or "",
                    f"{ab}_INTERPRETATION": val,
                }
                rows.append(rec)

    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    core = ["Organism", "Specimen date", "Specimen type", "Gender", "Age in years"]
    df = df.groupby(core, dropna=False, as_index=False).first()
    return df


