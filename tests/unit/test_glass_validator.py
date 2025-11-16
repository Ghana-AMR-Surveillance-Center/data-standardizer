import pandas as pd
from utils.glass_exporter import build_glass_export
from utils.glass_validator import validate_glass_df


def test_glass_validator_future_date_and_codes():
    df = pd.DataFrame(
        {
            "Country": ["ZA"],
            "Specimen date": ["2999-01-01"],
            "Specimen type": ["Blood"],
            "Organism": ["Escherichia coli"],
            "CiprofloxacinSIR": ["S"],
            "Age in years": [30],
            "Gender": ["F"],
            "Location type": ["Inpatient"],
            "Department": ["ICU"],
        }
    )
    g = build_glass_export(df)
    res = validate_glass_df(g)
    assert res["summary"]["errors"] >= 1  # future_specimen_date should be flagged


