"""Screening scores: generic thresholds, sector-aware thresholds, or rank within the compared companies."""
import numpy as np
import pandas as pd

from .config import SCORECARD, SECTOR_OVERRIDES

POINTS = {"🟢": 100, "🟡": 50, "🔴": 0}


def thresholds_for(sector, sector_aware):
    th = dict(SCORECARD)
    if sector_aware:
        th.update(SECTOR_OVERRIDES.get(sector, {}))
    return th


def rate(value, higher_better, good, ok):
    if pd.isna(value):
        return None
    if higher_better:
        return "🟢" if value >= good else "🟡" if value >= ok else "🔴"
    return "🟢" if value <= good else "🟡" if value <= ok else "🔴"


def icon_from_points(p):
    if pd.isna(p):
        return None
    return "🟢" if p >= 67 else "🟡" if p >= 34 else "🔴"


def threshold_scores(row, sector, sector_aware):
    """{metric: (value, icon, points)} using absolute thresholds."""
    out = {}
    for metric, (higher, good, ok) in thresholds_for(sector, sector_aware).items():
        value = row.get(metric, np.nan)
        icon = rate(value, higher, good, ok)
        out[metric] = (value, icon, POINTS.get(icon, np.nan))
    return out


def peer_points(latest):
    """latest: DataFrame (tickers x metrics). Returns 0-100 percentile rank of each company among its peers."""
    pts = pd.DataFrame(np.nan, index=latest.index, columns=latest.columns)
    for metric in latest.columns:
        col = latest[metric].astype(float).dropna()
        if len(col) < 2:
            continue
        higher = SCORECARD[metric][0]
        rank = col.rank(ascending=higher, method="average")
        pts.loc[col.index, metric] = (rank - 1) / (len(col) - 1) * 100
    return pts


def overall(points):
    vals = [p for p in points if pd.notna(p)]
    return float(np.mean(vals)) if vals else np.nan
