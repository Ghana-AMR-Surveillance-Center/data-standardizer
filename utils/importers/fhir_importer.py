"""
FHIR Importer (minimal)
Parses a FHIR Bundle (dict) with Patient, Specimen, and Observation resources
into a tabular DataFrame suitable for downstream standardization.

Assumptions (for minimal MVP):
- Patient.gender maps to 'Gender'
- Patient.birthDate used to estimate 'Age in years' if a specimen date is present
- Specimen.collection.collectedDateTime → 'Specimen date'; type.text → 'Specimen type'
- Observation.valueCodeableConcept.text or .coding[0].code → interpreted S/I/R when present
- Observation.code.text used to infer antibiotic code/name
"""

from __future__ import annotations

from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, date

from ..vocabularies import ANTIBIOTIC_SYNONYMS


def _antibiotic_from_text(text: str) -> Optional[str]:
    s = text.strip().lower()
    for code, syns in ANTIBIOTIC_SYNONYMS.items():
        for syn in syns:
            if syn in s:
                return code
    up = text.strip().upper()
    if 2 <= len(up) <= 4 and up.isalpha():
        return up
    return None


def import_fhir_bundle(bundle: Dict[str, Any]) -> pd.DataFrame:
    entries = bundle.get("entry", []) if isinstance(bundle, dict) else []
    patients: Dict[str, Dict[str, Any]] = {}
    specimens: Dict[str, Dict[str, Any]] = {}
    records: List[Dict[str, Any]] = []

    # First pass: index Patient and Specimen
    for e in entries:
        res = e.get("resource", {})
        if not isinstance(res, dict):
            continue
        rtype = res.get("resourceType")
        rid = res.get("id")
        if rtype == "Patient" and rid:
            patients[rid] = res
        elif rtype == "Specimen" and rid:
            specimens[rid] = res

    # Second pass: process Observations
    for e in entries:
        res = e.get("resource", {})
        if not isinstance(res, dict):
            continue
        if res.get("resourceType") != "Observation":
            continue

        # References
        subject_ref = res.get("subject", {}).get("reference", "")  # "Patient/{id}"
        specimen_ref = res.get("specimen", {}).get("reference", "")  # "Specimen/{id}"
        patient_id = subject_ref.split("/")[-1] if subject_ref else ""
        specimen_id = specimen_ref.split("/")[-1] if specimen_ref else ""

        pat = patients.get(patient_id, {})
        spc = specimens.get(specimen_id, {})

        # Observation code → antibiotic
        ab_text = ""
        code = res.get("code", {})
        if "text" in code and code["text"]:
            ab_text = code["text"]
        elif "coding" in code and code["coding"]:
            ab_text = code["coding"][0].get("display") or code["coding"][0].get("code") or ""

        antibiotic = _antibiotic_from_text(ab_text) if ab_text else None

        # Interpretation from valueCodeableConcept or valueString
        interp = None
        val_cc = res.get("valueCodeableConcept")
        if isinstance(val_cc, dict):
            if "text" in val_cc and val_cc["text"]:
                interp = val_cc["text"]
            elif "coding" in val_cc and val_cc["coding"]:
                interp = val_cc["coding"][0].get("code") or val_cc["coding"][0].get("display")
        if not interp and "valueString" in res:
            interp = res.get("valueString")

        # Specimen date
        spec_date = None
        collected = spc.get("collection", {}).get("collectedDateTime")
        if collected:
            try:
                spec_date = datetime.fromisoformat(collected.replace("Z", "+00:00")).date().isoformat()
            except Exception:
                spec_date = None

        # Specimen type
        spec_type = spc.get("type", {}).get("text") or ""

        # Patient gender and age (rough)
        gender = pat.get("gender", "")
        age_years = None
        bdate = pat.get("birthDate")
        if bdate and spec_date:
            try:
                bd = datetime.fromisoformat(bdate).date()
                sd = datetime.fromisoformat(spec_date).date()
                age_years = int((sd - bd).days / 365.25)
            except Exception:
                age_years = None

        rec = {
            "Organism": "",  # Often not explicit in FHIR Observation; left for later mapping
            "Specimen date": spec_date or "",
            "Specimen type": spec_type or "",
            "Gender": gender or "",
            "Age in years": age_years if age_years is not None else "",
        }
        if antibiotic and interp:
            rec[f"{antibiotic}_INTERPRETATION"] = str(interp).strip()
        records.append(rec)

    if not records:
        return pd.DataFrame()
    # Merge rows with same core fields (combine antibiotic columns)
    df = pd.DataFrame(records)
    core = ["Organism", "Specimen date", "Specimen type", "Gender", "Age in years"]
    other_cols = [c for c in df.columns if c not in core]
    if other_cols:
        df = df.groupby(core, dropna=False, as_index=False).first()
    return df


