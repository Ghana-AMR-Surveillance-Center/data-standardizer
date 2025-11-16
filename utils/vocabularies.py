"""
Lightweight organism and antibiotic vocabularies with synonyms.
Extensible; initial coverage focuses on common organisms/antibiotics.
"""

from __future__ import annotations

from typing import Dict, List

ORGANISM_SYNONYMS: Dict[str, List[str]] = {
    "ECO": ["escherichia coli", "e. coli", "e coli"],
    "KPN": ["klebsiella pneumoniae", "k. pneumoniae", "k pneumoniae"],
    "SAU": ["staphylococcus aureus", "s. aureus"],
    "PAE": ["pseudomonas aeruginosa", "p. aeruginosa"],
}

ANTIBIOTIC_SYNONYMS: Dict[str, List[str]] = {
    "CIP": ["ciprofloxacin", "cipro"],
    "GEN": ["gentamicin", "genta", "gent"],
    "AMK": ["amikacin"],
    "AMC": ["amoxicillin-clav", "amoxicillin clavulanate", "amox/clav"],
    "AMP": ["ampicillin"],
    "CAZ": ["ceftazidime"],
    "CRO": ["ceftriaxone"],
    "CXM": ["cefuroxime"],
    "FOX": ["cefoxitin"],
    "MEM": ["meropenem"],
    "SXT": ["co-trimoxasole", "trimethoprim/sulfamethoxazole", "cotrimoxazole"],
    "TCY": ["tetracycline"],
    "CHL": ["chloramphenicol"],
    "AZM": ["azithromycin"],
    "TZP": ["piperacillin/tazobactam", "pip/tazo"],
}

SPECIMEN_CODES: List[str] = ["BL", "UR", "SP", "CSF", "ST", "UNK"]


