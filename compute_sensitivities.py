"""
compute_sensitivities.py

Purpose
-------
Compute data-driven sensitivity stats from your OBK PARTS_DATABASE.

What it does
------------
1) Randomly samples many builds from the full database:
    (ENGINE, EXHAUST, SUSPENSION, GEARBOX, 2 distinct TRINKETS)
2) Computes total raw stats per build.
3) Computes robust stat deltas: P90 - P10 for each raw stat.
4) Computes per-score sensitivities using your *current* score formulas:
   sensitivity(stat in score) = coeff * (P90 - P10)
    (Direction is encoded directly in the coefficient sign; no LOWER_IS_BETTER table.)
5) Produces suggested "unit-balanced" coefficients:
    coeff ~ 1 / (P90 - P10), scaled so mean abs(coeff) ~= 1.0 (per score),
    then signed to match your current coefficients (so "lower is better" stays negative).

Usage
-----
- Put this file next to your app.py
- Edit APP_PY_PATH below (or leave default "app.py")
- Run:  python compute_sensitivities.py

Notes
-----
- This is Monte Carlo sampling (fast + robust). Exact enumeration can explode combinatorially.
- Increase N_SAMPLES for more stable estimates.
"""

from __future__ import annotations

import importlib.util
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


###############################################################
# CONFIG
###############################################################

APP_PY_PATH = "app.py"     # path to your Streamlit app containing PARTS_DATABASE
N_SAMPLES = 250_000        # increase if you want (e.g. 1_000_000)
SEED = 42

# Robust delta definition
P_LOW = 10
P_HIGH = 90

# If you renamed SlowAreaPenalty -> SlowDownSpd in your code, set this True.
# Otherwise it will fallback to SlowAreaPenalty if present.
USE_SLOWDOWNSPD_NAME = True


###############################################################
# LOAD PARTS_DATABASE FROM app.py
###############################################################

def load_parts_database_from_app(app_path: str) -> Dict:
    spec = importlib.util.spec_from_file_location("obk_app_module", app_path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Could not import app from path: {app_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore
    if not hasattr(mod, "PARTS_DATABASE"):
        raise AttributeError("app.py does not define PARTS_DATABASE")
    return getattr(mod, "PARTS_DATABASE")


###############################################################
# HELPERS
###############################################################

CATEGORIES = ["ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX", "TRINKET"]

RAW_STAT_KEYS = [
    "Speed", "StartBoost", "SlipStreamSpd",
    "SlowDownSpd" if USE_SLOWDOWNSPD_NAME else "SlowAreaPenalty",
    "StartCoins", "MaxCoins", "CoinBoostSpd", "CoinBoostTime",
    "DriftSteer", "Steer", "AirDriftTime",
    "UltCharge", "Daze", "SlipStreamRadius",
    "TrickSpd", "BoostPads", "MaxCoinsSpd", "SlipTime", "UltStart", "DriftRate",
    "T1", "T2", "T3",
]
RAW_STAT_KEYS = list(dict.fromkeys(RAW_STAT_KEYS))
KEY2IDX = {k: i for i, k in enumerate(RAW_STAT_KEYS)}


def df_from_category(parts_db: Dict, category: str, stat_keys: List[str]) -> pd.DataFrame:
    rows = []
    for item in parts_db.get(category, []):
        row = {"name": item.get("name", "")}
        stats = item.get("stats", {}) or {}
        for k in stat_keys:
            row[k] = float(stats.get(k, 0.0))
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=["name"] + list(stat_keys))
    return df


@dataclass
class ScoreSpec:
    name: str
    coeffs: Dict[str, float]


def percentile_delta(x , p_low, p_high):
    lo = float(np.percentile(x, p_low))
    hi = float(np.percentile(x, p_high))
    return lo, hi, hi - lo


def scaled_inverse_delta_coeffs(deltas):
    """
    Suggest coeffs ~ 1/delta, scaled so mean( abs(coeff) ) = 1.0.
    (We scale on absolute values; sign is applied later based on current coeff sign.)
    """
    inv_vals = []
    for _, d in deltas.items():
        if d > 1e-12:
            inv_vals.append(1.0 / d)

    if not inv_vals:
        return {k: 0.0 for k in deltas}

    mean_inv = float(np.mean(inv_vals))
    out = {}
    for k, d in deltas.items():
        if d <= 1e-12:
            out[k] = 0.0
        else:
            out[k] = (1.0 / d) / mean_inv
    return out


###############################################################
# MONTE CARLO BUILD SAMPLER
###############################################################

def sample_build_totals(
    parts_db,
    stat_keys,
    n_samples,
    seed
):
    """
    Returns:
        totals: (n_samples, K) raw stat totals
        dfs: dict[category] = DataFrame used
    """
    rng = np.random.default_rng(seed)

    dfs = {cat: df_from_category(parts_db, cat, stat_keys) for cat in CATEGORIES}

    for cat in ["ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX"]:
        if len(dfs[cat]) < 1:
            raise ValueError(f"Category {cat} has no items.")
    if len(dfs["TRINKET"]) < 2:
        raise ValueError("Need at least 2 trinkets to sample builds.")

    arrays = {cat: dfs[cat][stat_keys].to_numpy(np.float32) for cat in CATEGORIES}
    sizes = {cat: arrays[cat].shape[0] for cat in CATEGORIES}

    idx_e = rng.integers(0, sizes["ENGINE"], size=n_samples)
    idx_x = rng.integers(0, sizes["EXHAUST"], size=n_samples)
    idx_s = rng.integers(0, sizes["SUSPENSION"], size=n_samples)
    idx_g = rng.integers(0, sizes["GEARBOX"], size=n_samples)

    # Sample 2 distinct trinkets per build (vectorized with resample loop).
    idx_t1 = rng.integers(0, sizes["TRINKET"], size=n_samples)
    idx_t2 = rng.integers(0, sizes["TRINKET"], size=n_samples)
    mask_same = idx_t2 == idx_t1
    while mask_same.any():
        idx_t2[mask_same] = rng.integers(0, sizes["TRINKET"], size=int(mask_same.sum()))
        mask_same = idx_t2 == idx_t1

    totals = (
        arrays["ENGINE"][idx_e]
        + arrays["EXHAUST"][idx_x]
        + arrays["SUSPENSION"][idx_s]
        + arrays["GEARBOX"][idx_g]
        + arrays["TRINKET"][idx_t1]
        + arrays["TRINKET"][idx_t2]
    )
    return totals, dfs


###############################################################
# MAIN: compute sensitivities + suggested coefficients
###############################################################

def main():
    # Load DB
    try:
        parts_db = load_parts_database_from_app(APP_PY_PATH)
    except Exception as e:
        raise SystemExit(
            f"Failed to import PARTS_DATABASE from {APP_PY_PATH}.\n"
            f"Either fix APP_PY_PATH or paste PARTS_DATABASE into this script.\n\n"
            f"Error: {e}"
        )

    # Handle legacy naming fallback (if your DB still has SlowAreaPenalty)
    if USE_SLOWDOWNSPD_NAME:
        any_old = False
        for cat in CATEGORIES:
            for item in parts_db.get(cat, []):
                stats = item.get("stats", {}) or {}
                if "SlowAreaPenalty" in stats and "SlowDownSpd" not in stats:
                    any_old = True
                    stats["SlowDownSpd"] = stats.get("SlowAreaPenalty", 0.0)
                    item["stats"] = stats
        if any_old:
            print("[info] Mapped SlowAreaPenalty -> SlowDownSpd for sensitivity analysis.")

    # Define score specs
    # Coefficient SIGN is the single source of truth for direction.
    score_specs = [
        ScoreSpec("race", {
            "Speed": 2.8407310966678576,
            "SlipStreamSpd": 0.6266318396389959,
            "StartBoost": 0.42610965095451725,
            "SlowDownSpd": 0.10652741273862931,   # higher is better
            "BoostPads": 1.0,
            "TrickSpd": 1.0,
        }),
        ScoreSpec("coin", {
            "CoinBoostTime": 2.376095084387809,
            "StartCoins": 0.8078722947015423,
            "CoinBoostSpd": 0.4488179415008568,
            "MaxCoins": -0.36721467940979197,     # lower is better
        }),
        ScoreSpec("drift", {
            "AirDriftTime": 2.5183690692408747,
            "Steer": 0.25610533511237527,
            "DriftSteer": 0.22552559564674984,
            "DriftRate": 0.1214930052951624,      # higher is better
            "T1": 1.0,
            "T2": 1.0,
            "T3": 1.0,
        }),
        ScoreSpec("combat", {
            "UltCharge": 1.7704918032786885,
            "SlipStreamRadius": 0.7377049180327868,
            "Daze": -0.4918032786885246,          # lower is better (as currently set)
        }),
    ]

    # Sample totals
    totals, _dfs = sample_build_totals(parts_db, RAW_STAT_KEYS, N_SAMPLES, seed=SEED)
    print(f"[ok] Sampled builds: {totals.shape[0]:,}  |  raw stats: {totals.shape[1]}")

    # Compute P10/P90 deltas for each raw stat
    stat_rows = []
    deltas: Dict[str, float] = {}

    for k in RAW_STAT_KEYS:
        col = totals[:, KEY2IDX[k]].astype(np.float64)
        p10, p90, d = percentile_delta(col, P_LOW, P_HIGH)
        deltas[k] = d
        stat_rows.append({"stat": k, f"P{P_LOW}": p10, f"P{P_HIGH}": p90, "delta": d})

    df_stats = pd.DataFrame(stat_rows).sort_values("delta", ascending=False).reset_index(drop=True)

    # Score sensitivities (coeff * delta)
    sens_tables = []
    suggested_tables = []

    for spec in score_specs:
        rows = []
        score_delta_map: Dict[str, float] = {}

        for stat, c in spec.coeffs.items():
            if stat not in deltas:
                continue
            d = float(deltas[stat])

            sens = float(c) * d
            rows.append({
                "score": spec.name,
                "stat": stat,
                "coeff_current": float(c),
                "delta(P90-P10)": d,
                "sensitivity": sens,
                "abs_sensitivity": abs(sens),
                "direction": ("up_good" if c > 0 else ("down_good" if c < 0 else "neutral")),
            })
            score_delta_map[stat] = d

        df_s = pd.DataFrame(rows).sort_values("abs_sensitivity", ascending=False).reset_index(drop=True)
        sens_tables.append(df_s)

        # Suggested coeffs that equalize contribution per typical delta: coeff ~ 1/delta
        inv = scaled_inverse_delta_coeffs(score_delta_map)

        # Sign the suggested coefficients to match the current coefficient signs
        for stat in list(inv.keys()):
            cur = float(spec.coeffs.get(stat, 0.0))
            if cur == 0.0:
                inv[stat] = 0.0
            else:
                inv[stat] = math.copysign(abs(inv[stat]), cur)

        df_sug = pd.DataFrame(
            [
                {
                    "score": spec.name,
                    "stat": k,
                    "coeff_suggested_unit_balanced": float(v),
                    "delta(P90-P10)": float(score_delta_map[k]),
                }
                for k, v in inv.items()
            ]
        ).sort_values("coeff_suggested_unit_balanced", ascending=False).reset_index(drop=True)
        suggested_tables.append(df_sug)

    df_sens_all = pd.concat(sens_tables, ignore_index=True)
    df_sug_all = pd.concat(suggested_tables, ignore_index=True)

    # Output
    pd.set_option("display.width", 140)
    pd.set_option("display.max_columns", 50)

    print("\n=== RAW STAT ROBUST RANGES (sampled builds) ===")
    print(df_stats.to_string(index=False))

    print("\n=== CURRENT COEFF * DELTA SENSITIVITIES (by score) ===")
    for spec in score_specs:
        df_sub = df_sens_all[df_sens_all["score"] == spec.name].copy()
        print(f"\n--- {spec.name.upper()} ---")
        print(df_sub.to_string(index=False))

    print("\n=== SUGGESTED UNIT-BALANCED COEFFS (per score) ===")
    for spec in score_specs:
        df_sub = df_sug_all[df_sug_all["score"] == spec.name].copy()
        print(f"\n--- {spec.name.upper()} ---")
        print(df_sub.to_string(index=False))

    # Save CSVs
    df_stats.to_csv("sens_raw_stat_ranges.csv", index=False)
    df_sens_all.to_csv("sens_current_coeff_sensitivities.csv", index=False)
    df_sug_all.to_csv("sens_suggested_unit_balanced_coeffs.csv", index=False)
    print("\n[ok] Wrote:")
    print("  - sens_raw_stat_ranges.csv")
    print("  - sens_current_coeff_sensitivities.csv")
    print("  - sens_suggested_unit_balanced_coeffs.csv")

    # Optional: print a ready-to-paste coeff dict block
    print("\n=== READY-TO-PASTE COEFF DICTS (unit-balanced baseline) ===")
    for spec in score_specs:
        df_sub = df_sug_all[df_sug_all["score"] == spec.name]
        d = {row["stat"]: float(row["coeff_suggested_unit_balanced"]) for _, row in df_sub.iterrows()}
        print(f"\n{spec.name.upper()}_COEFFS = {d}")


if __name__ == "__main__":
    main()
