import pandas as pd
from utils.breakpoint_interpreter import interpret_value, apply_interpretation_to_dataframe


def test_interpret_value_examples():
    # E. coli CIP MIC example seeded in registry
    assert interpret_value("ECO", "CIP", "mic", 0.5, None, "CLSI", "2024") == "S"
    assert interpret_value("ECO", "CIP", "mic", 1.0, None, "CLSI", "2024") == "S"
    assert interpret_value("ECO", "CIP", "mic", 2.0, None, "CLSI", "2024") == "I"
    assert interpret_value("ECO", "CIP", "mic", 4.0, None, "CLSI", "2024") == "R"

    # Zone
    assert interpret_value("ECO", "CIP", "zone", 22, None, "CLSI", "2024") == "S"
    assert interpret_value("ECO", "CIP", "zone", 16, None, "CLSI", "2024") == "I"
    assert interpret_value("ECO", "CIP", "zone", 12, None, "CLSI", "2024") == "R"


def test_apply_interpretation_to_dataframe():
    df = pd.DataFrame({
        "Organism": ["ECO", "KPN"],
        "CIP_NM": [1.0, None],
        "CAZ_ND": [None, 15.0]
    })
    out = apply_interpretation_to_dataframe(
        df, organism_col="Organism",
        method_cols={"mic": ["CIP_NM"], "zone": ["CAZ_ND"]},
        standard="CLSI", version="2024"
    )
    assert "CIP_INTERPRETATION" in out.columns
    assert out.loc[0, "CIP_INTERPRETATION"] in {"S","I","R","Not Tested"}
    assert "CAZ_INTERPRETATION" in out.columns
    assert out.loc[1, "CAZ_INTERPRETATION"] in {"S","I","R","Not Tested"}


