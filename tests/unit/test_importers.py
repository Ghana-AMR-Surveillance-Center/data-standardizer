import pandas as pd
from utils.importers.fhir_importer import import_fhir_bundle
from utils.importers.hl7_importer import import_hl7_message


def test_import_fhir_bundle_minimal():
    bundle = {
        "resourceType": "Bundle",
        "entry": [
            {"resource": {"resourceType": "Patient", "id": "p1", "gender": "female", "birthDate": "1990-01-01"}},
            {"resource": {"resourceType": "Specimen", "id": "s1", "type": {"text": "Blood"}, "collection": {"collectedDateTime": "2025-01-01T00:00:00Z"}}},
            {"resource": {"resourceType": "Observation", "id": "o1",
                          "subject": {"reference": "Patient/p1"},
                          "specimen": {"reference": "Specimen/s1"},
                          "code": {"text": "Ciprofloxacin"},
                          "valueCodeableConcept": {"text": "S"}}}
        ]
    }
    df = import_fhir_bundle(bundle)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "CIP_INTERPRETATION" in df.columns


def test_import_hl7_message_minimal():
    msg = "MSH|^~\\&|LIS|HOSP|AMR|HOSP|202501010000||ORU^R01|123|P|2.5\r\n" \
          "PID|1||12345||DOE^JANE||19800101|F\r\n" \
          "OBR|1|||MIC PANEL|||20250101||||||Blood\r\n" \
          "OBX|1|ST|CIP^Ciprofloxacin^LN||S\r\n"
    df = import_hl7_message(msg)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "CIP_INTERPRETATION" in df.columns


