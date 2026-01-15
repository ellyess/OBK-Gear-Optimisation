"""
Optimiser module for OBK Gear Optimiser.
Includes functions and classes for performing gear optimisation.
"""

from dataclasses import dataclass, field
import numpy as np
import pandas as pd

from .constants import RAW_STAT_KEYS, KEY2IDX
from .data import df_from_category
from .scoring import compute_main_scores
from .ranges import estimate_main_score_ranges, estimate_raw_stat_ranges

@dataclass
class OptimiseConfig:
    top_n: int = 20
    weights_main: dict = field(default_factory=dict)
    weights_raw: dict = field(default_factory=dict)
    constraints_main: dict = field(default_factory=dict)
    constraints_raw: dict = field(default_factory=dict)
    normalize_objective: bool = True

    # NEW: diversity settings
    diverse: bool = True
    min_diff_parts: int = 2
    per_part_max: dict | None = None

PART_COLS = ["ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX", "TRINKET_1", "TRINKET_2"]

def _hamming_parts(row_a, row_b, part_cols=PART_COLS) -> int:
    return sum(row_a[c] != row_b[c] for c in part_cols)

def _diversify_by_parts(
    df: pd.DataFrame,
    top_n: int,
    *,
    min_diff_parts: int = 2,
    per_part_max: dict | None = None,
    part_cols=PART_COLS,
) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.sort_values("objective", ascending=False).reset_index(drop=True)

    selected = []
    counts = {c: {} for c in part_cols}

    def ok_quota(i: int) -> bool:
        if not per_part_max:
            return True
        row = df.loc[i]
        for col, lim in per_part_max.items():
            if col not in part_cols or lim is None:
                continue
            v = row[col]
            if counts[col].get(v, 0) >= int(lim):
                return False
        return True

    def add(i: int):
        row = df.loc[i]
        selected.append(i)
        for c in part_cols:
            v = row[c]
            counts[c][v] = counts[c].get(v, 0) + 1

    add(0)  # best first
    cur_min = int(min_diff_parts)

    while len(selected) < int(top_n) and len(selected) < len(df):
        picked = False

        for i in range(1, len(df)):
            if i in selected:
                continue
            if not ok_quota(i):
                continue
            row_i = df.loc[i]
            if all(_hamming_parts(row_i, df.loc[j], part_cols) >= cur_min for j in selected):
                add(i)
                picked = True
                if len(selected) >= int(top_n):
                    break

        if not picked:
            if cur_min > 0:
                cur_min -= 1  # relax requirement
            else:
                # fill remaining by objective (still respecting quotas)
                for i in range(1, len(df)):
                    if i in selected:
                        continue
                    if not ok_quota(i):
                        continue
                    add(i)
                    if len(selected) >= int(top_n):
                        break
                break

    return df.loc[selected].reset_index(drop=True)


def optimise_builds(inventory, config):
    if not config.weights_main:
        config.weights_main = {"race": 1.0, "coin": 1.0, "drift": 1.0, "combat": 1.0}
    if config.weights_raw is None:
        config.weights_raw = {}
    if config.constraints_main is None:
        config.constraints_main = {}
    if config.constraints_raw is None:
        config.constraints_raw = {}

    stat_keys = tuple(RAW_STAT_KEYS)
    dfE = df_from_category("ENGINE", stat_keys)
    dfX = df_from_category("EXHAUST", stat_keys)
    dfS = df_from_category("SUSPENSION", stat_keys)
    dfG = df_from_category("GEARBOX", stat_keys)
    dfT = df_from_category("TRINKET", stat_keys)

    def _filter(df, names, cat):
        out = df[df["name"].isin(set(names))].reset_index(drop=True)
        if out.empty:
            raise ValueError(f"No selected parts in {cat}. Select at least 1.")
        return out

    dfE = _filter(dfE, inventory["ENGINE"], "ENGINE")
    dfX = _filter(dfX, inventory["EXHAUST"], "EXHAUST")
    dfS = _filter(dfS, inventory["SUSPENSION"], "SUSPENSION")
    dfG = _filter(dfG, inventory["GEARBOX"], "GEARBOX")
    dfT = _filter(dfT, inventory["TRINKET"], "TRINKET")

    MINIMISE_RAW = {"MaxCoins", "Daze"}  # lower is better for these

    def _minmax_norm(x, lo, hi):
        denom = (hi - lo)
        if denom <= 1e-9:
            return np.zeros_like(x, dtype=np.float32)
        y = (x - lo) / denom
        return np.clip(y, 0.0, 1.0).astype(np.float32)

    norm_on = bool(getattr(config, "normalize_objective", True))

    if norm_on:
        main_ranges = estimate_main_score_ranges(dfE, dfX, dfS, dfG, dfT)
        raw_keys_needed = [k for k in (config.weights_raw or {}).keys() if k in KEY2IDX]
        raw_ranges = estimate_raw_stat_ranges(dfE, dfX, dfS, dfG, dfT, raw_keys_needed) if raw_keys_needed else {}

    if len(dfT) < 2:
        raise ValueError("Select at least 2 trinkets (duplicates are not allowed).")

    E_arr = dfE[RAW_STAT_KEYS].to_numpy(np.float32)
    X_arr = dfX[RAW_STAT_KEYS].to_numpy(np.float32)
    S_arr = dfS[RAW_STAT_KEYS].to_numpy(np.float32)
    G_arr = dfG[RAW_STAT_KEYS].to_numpy(np.float32)
    T_arr = dfT[RAW_STAT_KEYS].to_numpy(np.float32)

    E, X, S, G, T = len(dfE), len(dfX), len(dfS), len(dfG), len(dfT)

    idx_e = np.repeat(np.arange(E), X * S * G)
    idx_x = np.tile(np.repeat(np.arange(X), S * G), E)
    idx_s = np.tile(np.repeat(np.arange(S), G), E * X)
    idx_g = np.tile(np.arange(G), E * X * S)

    base = E_arr[idx_e] + X_arr[idx_x] + S_arr[idx_s] + G_arr[idx_g]
    nbase = base.shape[0]

    t1, t2 = np.triu_indices(T, k=1)
    pair_stats = T_arr[t1] + T_arr[t2]

    results = []
    top_n = int(config.top_n)

    for p_i in range(pair_stats.shape[0]):
        totals = base + pair_stats[p_i]
        scores = compute_main_scores(totals)

        mask = np.ones(nbase, dtype=bool)

        for k, (lo, hi) in config.constraints_main.items():
            if lo is not None:
                mask &= scores[k] >= float(lo)
            if hi is not None:
                mask &= scores[k] <= float(hi)

        for raw, (lo, hi) in config.constraints_raw.items():
            if raw not in KEY2IDX:
                continue
            col = totals[:, KEY2IDX[raw]]
            if lo is not None:
                mask &= col >= float(lo)
            if hi is not None:
                mask &= col <= float(hi)

        if not mask.any():
            continue

        obj = np.zeros(nbase, dtype=np.float32)

        # MAIN SCORES
        for k, w in (config.weights_main or {}).items():
            w = float(w)
            if w == 0:
                continue

            x = scores[k].astype(np.float32)
            if norm_on:
                lo, hi = main_ranges.get(k, (float(x.min()), float(x.max())))
                x = _minmax_norm(x, float(lo), float(hi))
            obj += w * x

        # RAW STATS
        for raw, w in (config.weights_raw or {}).items():
            if raw not in KEY2IDX:
                continue

            w = float(w)
            if w == 0:
                continue

            x = totals[:, KEY2IDX[raw]].astype(np.float32)
            if norm_on:
                lo, hi = raw_ranges.get(raw, (float(x.min()), float(x.max())))
                x = _minmax_norm(x, float(lo), float(hi))

            if raw in MINIMISE_RAW:
                x = 1.0 - x if norm_on else -x

            obj += w * x

        obj[~mask] = -np.inf
        kkeep = min(max(top_n * 20, top_n), int(mask.sum()))
        cand = np.argpartition(obj, -kkeep)[-kkeep:]
        cand = cand[np.argsort(obj[cand])[::-1]]

        for i in cand[:kkeep]:
            results.append((
                float(obj[i]),
                float(scores["race"][i]),
                float(scores["coin"][i]),
                float(scores["drift"][i]),
                float(scores["combat"][i]),
                dfE.loc[idx_e[i], "name"],
                dfX.loc[idx_x[i], "name"],
                dfS.loc[idx_s[i], "name"],
                dfG.loc[idx_g[i], "name"],
                dfT.loc[t1[p_i], "name"],
                dfT.loc[t2[p_i], "name"],
            ))

    cols = [
        "objective", "race", "coin", "drift", "combat",
        "ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX",
        "TRINKET_1", "TRINKET_2",
    ]
    if not results:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(results, columns=cols)
    df = df.sort_values("objective", ascending=False).drop_duplicates(
        subset=PART_COLS
    ).reset_index(drop=True)

    if getattr(config, "diverse", False):
        df = _diversify_by_parts(
            df,
            top_n=int(top_n),
            min_diff_parts=int(getattr(config, "min_diff_parts", 2)),
            per_part_max=getattr(config, "per_part_max", None),
        )
    else:
        df = df.head(top_n).reset_index(drop=True)

    return df

