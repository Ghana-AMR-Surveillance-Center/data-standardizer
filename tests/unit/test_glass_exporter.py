import pandas as pd
from utils.glass_exporter import build_glass_export, GLASS_COLUMNS


def test_build_glass_export_minimal():
    df = pd.DataFrame(
        {
            "Country": ["ZA", "ZA"],
            "Specimen date": ["2025-01-04", "2025-01-04"],
            "Specimen type": ["Blood", "Urine"],
            "Organism": ["Escherichia coli", "Klebsiella pneumoniae"],
            "CiprofloxacinSIR": ["S", "I"],
            "GentamicinSIR": ["R", None],
            "Age in years": [34, 52],
            "Gender": ["F", "M"],
            "Location type": ["Inpatient", "Outpatient"],
            "Department": ["ICU", "OPD"],
        }
    )

    out = build_glass_export(df)
    assert list(out.columns) == GLASS_COLUMNS
    # Expect three rows: 2 antibiotics for row 0; 1 for row 1
    assert len(out) == 3

    # Check a representative row
    r0 = out.iloc[0]
    assert r0["COUNTRY"] == "ZA"
    assert r0["SPECIMEN"] in {"BL", "UR"}
    assert r0["ORGANISM"] in {"ECO", "KPN"}
    assert r0["ANTIBIOTIC"] in {"CIP", "GEN"}
    assert r0["INTERPRETATION"] in {"S", "I", "R"}
    assert r0["AGE"] in {34, 52}
    assert r0["SEX"] in {"F", "M", "U"}
    assert r0["PATIENT_TYPE"] in {"IN", "OUT", "UNK"}
    assert r0["WARD"] in {"ICU", "OPD"}


