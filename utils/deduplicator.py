"""
Episode-based Deduplicator
Keeps the first isolate per patient+organism within a configurable time window.
Adds a 'Deduplicated' boolean column to indicate removed rows if desired.
"""

from __future__ import annotations

from typing import Optional
import pandas as pd


def deduplicate_by_episode(
    df: pd.DataFrame,
    patient_col: str,
    organism_col: str,
    date_col: str,
    window_days: int = 30,
    mark_only: bool = False,
) -> pd.DataFrame:
    """
    Deduplicate isolates per (patient, organism) episode within window_days.
    If mark_only is True, returns original df with a 'Deduplicated' column.
    Otherwise, returns a filtered df keeping only the first isolate per episode.
    """
    if any(c not in df.columns for c in (patient_col, organism_col, date_col)):
        return df.copy()

    work = df.copy()
    work[date_col] = pd.to_datetime(work[date_col], errors="coerce")

    work.sort_values([patient_col, organism_col, date_col], inplace=True, kind="mergesort")
    work["Deduplicated"] = False

    last_kept_date = {}
    for idx, row in work.iterrows():
        pid = row[patient_col]
        org = row[organism_col]
        cdate = row[date_col]
        key = (pid, org)
        if pd.isna(cdate):
            # keep rows with unknown date (cannot dedup confidently)
            last_kept_date[key] = cdate
            continue

        if key not in last_kept_date:
            last_kept_date[key] = cdate
            continue

        prev = last_kept_date[key]
        if pd.isna(prev) or (cdate - prev).days > window_days:
            last_kept_date[key] = cdate
        else:
            work.at[idx, "Deduplicated"] = True

    if mark_only:
        return work
    return work[~work["Deduplicated"]].copy().drop(columns=["Deduplicated"])


