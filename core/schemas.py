from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, constr, conint, confloat


class Patient(BaseModel):
    patient_id: Optional[str] = None
    sex: Optional[Literal["M", "F", "O", "U"]] = None
    age_years: Optional[confloat(ge=0, le=120)] = None
    location_country: Optional[constr(pattern=r"^[A-Z]{2}$")] = None
    facility_id: Optional[str] = None
    inpatient_outpatient: Optional[Literal["I", "O", "U"]] = None


class Specimen(BaseModel):
    specimen_id: Optional[str] = None
    specimen_type: Optional[str] = None
    collection_date: Optional[str] = Field(default=None, description="ISO date (YYYY-MM-DD)")
    ward: Optional[str] = None


class Isolate(BaseModel):
    isolate_id: Optional[str] = None
    organism_text: Optional[str] = None
    organism_code: Optional[str] = None
    report_date: Optional[str] = None
    episode_id: Optional[str] = None


class ASTResult(BaseModel):
    antibiotic_text: Optional[str] = None
    antibiotic_code: Optional[str] = None
    test_type: Optional[Literal["mic", "zone", "rsi"]] = None
    mic_value: Optional[float] = None
    mic_comparator: Optional[Literal["<", "≤", "=", "≥", ">"]] = None
    zone_mm: Optional[float] = None
    interpretation: Optional[Literal["S", "I", "R", "Not Tested"]] = None
    breakpoint_standard: Optional[Literal["CLSI", "EUCAST"]] = None
    breakpoint_version: Optional[str] = None


class Provenance(BaseModel):
    import_source: Optional[str] = None
    import_timestamp: Optional[str] = None
    rule_version: Optional[str] = None
    mapping_template_id: Optional[str] = None
    lineage_id: Optional[str] = None


class CanonicalAMRRecord(BaseModel):
    patient: Patient
    specimen: Specimen
    isolate: Isolate
    ast_results: List[ASTResult]
    provenance: Provenance


class GlassRow(BaseModel):
    COUNTRY: Optional[constr(pattern=r"^[A-Z]{2}$")] = None
    SPECIMENDATE: Optional[str] = None
    SPECIMEN: Optional[str] = None
    ORGANISM: Optional[constr(pattern=r"^[A-Z]{2,4}$")] = None
    ANTIBIOTIC: Optional[constr(pattern=r"^[A-Z]{2,4}$")] = None
    INTERPRETATION: Optional[Literal["S", "I", "R"]] = None
    AGE: Optional[conint(ge=0, le=120)] = None
    SEX: Optional[Literal["M", "F", "U"]] = None
    PATIENT_TYPE: Optional[Literal["IN", "OUT", "UNK"]] = None
    WARD: Optional[str] = None


