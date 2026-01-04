"""
Scoring functions for OBK Gear Optimiser.
"""

import numpy as np
import pandas as pd
import streamlit as st

from .constants import (
    KEY2IDX, RAW_STAT_KEYS, MAIN_SCORES,
    RACE_COEFFS, COIN_COEFFS, DRIFT_COEFFS, COMBAT_COEFFS,
)
from .data import df_from_category

def compute_main_scores(totals):
    scores = {}
    score_maps = {
        "race": RACE_COEFFS,
        "coin": COIN_COEFFS,
        "drift": DRIFT_COEFFS,
        "combat": COMBAT_COEFFS,
    }

    for score_name, coeffs in score_maps.items():
        s = np.zeros(totals.shape[0], dtype=np.float32)
        for stat, coeff in coeffs.items():
            idx = KEY2IDX.get(stat)
            if idx is None:
                continue
            s += float(coeff) * totals[:, idx]
        scores[score_name] = s
    return scores

def _linear_score_df(df, coeffs):
    if df.empty:
        return np.array([], dtype=np.float32)
    s = np.zeros(len(df), dtype=np.float32)
    for k, c in coeffs.items():
        if k in df.columns:
            s += float(c) * df[k].to_numpy(np.float32)
    return s

@st.cache_data(show_spinner=False)
def compute_global_score_maxima():
    stat_keys = tuple(RAW_STAT_KEYS)
    dfE = df_from_category("ENGINE", stat_keys)
    dfX = df_from_category("EXHAUST", stat_keys)
    dfS = df_from_category("SUSPENSION", stat_keys)
    dfG = df_from_category("GEARBOX", stat_keys)
    dfT = df_from_category("TRINKET", stat_keys)

    def best_single(df, coeffs):
        s = _linear_score_df(df, coeffs)
        return float(s.max()) if s.size else 0.0

    def best_two_trinkets(dfT_, coeffs):
        s = _linear_score_df(dfT_, coeffs)
        if s.size < 2:
            return 0.0
        top2 = np.partition(s, -2)[-2:]
        return float(top2.sum())

    maxima = {
        "race": best_single(dfE, RACE_COEFFS) + best_single(dfX, RACE_COEFFS) + best_single(dfS, RACE_COEFFS) + best_single(dfG, RACE_COEFFS) + best_two_trinkets(dfT, RACE_COEFFS),
        "coin": best_single(dfE, COIN_COEFFS) + best_single(dfX, COIN_COEFFS) + best_single(dfS, COIN_COEFFS) + best_single(dfG, COIN_COEFFS) + best_two_trinkets(dfT, COIN_COEFFS),
        "drift": best_single(dfE, DRIFT_COEFFS) + best_single(dfX, DRIFT_COEFFS) + best_single(dfS, DRIFT_COEFFS) + best_single(dfG, DRIFT_COEFFS) + best_two_trinkets(dfT, DRIFT_COEFFS),
        "combat": best_single(dfE, COMBAT_COEFFS) + best_single(dfX, COMBAT_COEFFS) + best_single(dfS, COMBAT_COEFFS) + best_single(dfG, COMBAT_COEFFS) + best_two_trinkets(dfT, COMBAT_COEFFS),
    }
    return maxima

def normalize_scores_global(df):
    df = df.copy()
    max_scores = compute_global_score_maxima()
    for k in MAIN_SCORES:
        vmax = float(max_scores.get(k, 0.0))
        df[f"{k}_raw"] = df[k].astype(float)
        df[f"{k}_max"] = vmax
        if vmax > 0:
            df[f"{k}_norm"] = (df[k].astype(float) / vmax) * 100.0
        else:
            df[f"{k}_norm"] = 0.0
    return df
