"""
Estimate stat ranges for OBK Gear Optimiser.
"""

import numpy as np

from .constants import (
    RACE_COEFFS, COIN_COEFFS, DRIFT_COEFFS, COMBAT_COEFFS
)

def _minmax(df, keys):
    mn, mx = {}, {}
    for k in keys:
        mn[k] = float(df[k].min()) if (not df.empty and k in df.columns) else 0.0
        mx[k] = float(df[k].max()) if (not df.empty and k in df.columns) else 0.0
    return mn, mx

def _trinket_pair_minmax(dfT, keys):
    arr = dfT[keys].to_numpy(np.float32)
    T = len(dfT)
    t1, t2 = np.triu_indices(T, k=1)
    pairs = arr[t1] + arr[t2]
    mn = {k: float(pairs[:, i].min()) for i, k in enumerate(keys)}
    mx = {k: float(pairs[:, i].max()) for i, k in enumerate(keys)}
    return mn, mx

def _lin_minmax(total_min, total_max, coeffs):
    lo, hi = 0.0, 0.0
    for k, c in coeffs.items():
        if c >= 0:
            lo += c * total_min.get(k, 0.0)
            hi += c * total_max.get(k, 0.0)
        else:
            lo += c * total_max.get(k, 0.0)
            hi += c * total_min.get(k, 0.0)
    return float(lo), float(hi)

def estimate_main_score_ranges(dfE, dfX, dfS, dfG, dfT):
    needed = list(set(list(RACE_COEFFS) + list(COIN_COEFFS) + list(DRIFT_COEFFS) + list(COMBAT_COEFFS)))
    e_mn, e_mx = _minmax(dfE, needed)
    x_mn, x_mx = _minmax(dfX, needed)
    s_mn, s_mx = _minmax(dfS, needed)
    g_mn, g_mx = _minmax(dfG, needed)
    t_mn, t_mx = _trinket_pair_minmax(dfT, needed)

    total_min = {k: e_mn[k] + x_mn[k] + s_mn[k] + g_mn[k] + t_mn[k] for k in needed}
    total_max = {k: e_mx[k] + x_mx[k] + s_mx[k] + g_mx[k] + t_mx[k] for k in needed}

    rng = {
        "race": _lin_minmax(total_min, total_max, RACE_COEFFS),
        "coin": _lin_minmax(total_min, total_max, COIN_COEFFS),
        "drift": _lin_minmax(total_min, total_max, DRIFT_COEFFS),
        "combat": _lin_minmax(total_min, total_max, COMBAT_COEFFS),
    }
    out = {}
    for k, (lo, hi) in rng.items():
        pad = max(1.0, 0.05 * (hi - lo) if hi > lo else 1.0)
        out[k] = (lo - pad, hi + pad)
    return out

def estimate_raw_stat_ranges(dfE, dfX, dfS, dfG, dfT, keys):
    e_mn, e_mx = _minmax(dfE, keys)
    x_mn, x_mx = _minmax(dfX, keys)
    s_mn, s_mx = _minmax(dfS, keys)
    g_mn, g_mx = _minmax(dfG, keys)
    t_mn, t_mx = _trinket_pair_minmax(dfT, keys)

    out = {}
    for k in keys:
        lo = e_mn[k] + x_mn[k] + s_mn[k] + g_mn[k] + t_mn[k]
        hi = e_mx[k] + x_mx[k] + s_mx[k] + g_mx[k] + t_mx[k]
        pad = max(0.1, 0.05 * (hi - lo) if hi > lo else 0.1)
        out[k] = (float(lo - pad), float(hi + pad))
    return out
