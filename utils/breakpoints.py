"""
Breakpoint registry for CLSI/EUCAST with versioning.

This is a minimal, extensible structure intended as a starting point.
Keys:
  (standard, version, organism_code, antibiotic_code, method)
Values:
  dict with numeric thresholds appropriate to the method.

MIC example (lower is more susceptible):
  {"mic_s_le": 1, "mic_i_le": 2}
Zone example (larger zone is more susceptible):
  {"zone_s_ge": 21, "zone_i_ge": 16}
"""

from __future__ import annotations

from typing import Dict, Tuple

BreakpointKey = Tuple[str, str, str, str, str]

_REGISTRY: Dict[BreakpointKey, Dict[str, float]] = {}


def _seed_minimal() -> None:
    # CLSI 2024 examples (illustrative only; not authoritative)
    entries = {
        ("CLSI", "2024", "ECO", "CIP", "mic"): {"mic_s_le": 1.0, "mic_i_le": 2.0},
        ("CLSI", "2024", "ECO", "CIP", "zone"): {"zone_s_ge": 21.0, "zone_i_ge": 16.0},
        ("CLSI", "2024", "KPN", "CAZ", "zone"): {"zone_s_ge": 18.0, "zone_i_ge": 15.0},
        ("CLSI", "2024", "ECO", "GEN", "zone"): {"zone_s_ge": 15.0, "zone_i_ge": 13.0},
    }
    _REGISTRY.update(entries)

    # EUCAST 2024 examples (illustrative only; not authoritative)
    eucast = {
        ("EUCAST", "2024", "ECO", "CIP", "mic"): {"mic_s_le": 0.5, "mic_i_le": 1.0},
        ("EUCAST", "2024", "ECO", "CIP", "zone"): {"zone_s_ge": 25.0, "zone_i_ge": 22.0},
        ("EUCAST", "2024", "KPN", "CAZ", "zone"): {"zone_s_ge": 20.0, "zone_i_ge": 17.0},
    }
    _REGISTRY.update(eucast)


def registry_get(standard: str, version: str, organism: str, antibiotic: str, method: str) -> Dict[str, float] | None:
    return _REGISTRY.get((standard.upper(), version, organism.upper(), antibiotic.upper(), method.lower()))


def upsert_breakpoint(standard: str, version: str, organism: str, antibiotic: str, method: str, data: Dict[str, float]) -> None:
    _REGISTRY[(standard.upper(), version, organism.upper(), antibiotic.upper(), method.lower())] = data


def available_versions(standard: str) -> Dict[str, int]:
    # Returns mapping of version -> count entries
    out: Dict[str, int] = {}
    for (std, ver, *_), v in _REGISTRY.items():
        if std == standard.upper():
            out[ver] = out.get(ver, 0) + 1
    return out


_seed_minimal()


