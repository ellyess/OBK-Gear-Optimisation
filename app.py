"""
Application: OBK Gear Optimiser
Author: Ellyess
Date: 2025-12-30
Description:
    A Streamlit app to optimise OBK gear builds based on user-defined priorities and constraints.

Run:
    conda env create -f environment.yaml
    conda activate OBK-gear
    streamlit run app.py
"""

import numpy as np
import pandas as pd
import streamlit as st

from obk.styles import APP_CSS, LEGEND_CSS, LEGEND_HTML
from obk.constants import (
    CATEGORIES, RAW_STAT_KEYS, KEY2IDX, MAIN_SCORES,
    PRIORITY_MAP, RAW_CONSTRAINT_DEFAULTS, PRESETS,
    RAW_UI_LABELS,
)
from obk.data import df_from_category, PARTS_DATABASE
from obk.ui_state import (
    init_owned_state, part_toggle_grid, set_all_owned,
    apply_import_replace, make_run_signature
)
from obk.ui_render import (
    render_build_table, render_compare_panel,
)
from obk.optimiser import OptimiseConfig, optimise_builds
from obk.scoring import normalize_scores_global


###############################################################
# APP
###############################################################
st.set_page_config(page_title="Parts Build Optimiser", layout="wide")
st.markdown(APP_CSS, unsafe_allow_html=True)
st.markdown(LEGEND_CSS, unsafe_allow_html=True)

st.title("OBK Gear Optimiser")
st.caption("By Ellyess")

missing = [c for c in CATEGORIES if c not in PARTS_DATABASE]
if missing:
    st.error(f"PARTS_DATABASE missing categories: {missing}. Paste your full database at the top of obk/data.py.")
    st.stop()

stat_keys = tuple(RAW_STAT_KEYS)
names_by_cat = {
    cat: sorted(df_from_category(cat, stat_keys)["name"].astype(str).tolist(), key=lambda x: x.lower())
    for cat in CATEGORIES
}
init_owned_state(names_by_cat)

# Sidebar: import first
st.sidebar.header("0) Import owned equipment (paste list)")
st.sidebar.caption("Paste names separated by newlines or commas. Unknown names will be reported.")
st.sidebar.text_area(
    "Owned equipment list",
    key="import_text",
    height=120,
    placeholder="e.g.\nFresh Engine\nCyber Exhaust\nLucky Dice"
)

if st.sidebar.button("Replace owned with this list", use_container_width=True):
    applied, unknown, amb = apply_import_replace(st.session_state.get("import_text", ""), names_by_cat)
    if unknown:
        st.sidebar.error("Unknown names:\n- " + "\n- ".join(unknown[:25]) + ("" if len(unknown) <= 25 else "\n…"))
    if amb:
        st.sidebar.warning("Ambiguous names (exist in multiple categories):\n- " + "\n- ".join(amb[:25]) + ("" if len(amb) <= 25 else "\n…"))
    if applied > 0:
        st.sidebar.success(f"Applied {applied} items.")
    st.rerun()

st.sidebar.markdown("---")

# Sidebar: inventory selection
st.sidebar.header("1) Click to select what you have")
inventory = {cat: part_toggle_grid(cat, names_by_cat[cat]) for cat in CATEGORIES}

# Select/Clear buttons
st.sidebar.markdown("---")
q1, q2 = st.sidebar.columns(2)
with q1:
    if st.button("Select all"):
        set_all_owned(True, names_by_cat)
        st.rerun()
with q2:
    if st.button("Clear all"):
        set_all_owned(False, names_by_cat)
        st.rerun()

# Priorities
st.sidebar.markdown("---")
st.sidebar.header("2) Priority")
st.sidebar.caption("Higher priority means the optimiser will favour builds that perform better in that area. (Low = 1.0x, Medium = 2.5x, High = 5x)")

normalize_objective = st.sidebar.checkbox(
    "Normalise stats (recommended)",
    value=True,
    help="When enabled, optimisation uses 0–1 normalised values (based on achievable ranges from your selected inventory). This avoids mixed-unit stats dominating the objective."
)

# Preset UI
preset_name = st.sidebar.selectbox("Preset", list(PRESETS.keys()), key="preset_name")
if st.sidebar.button("Apply preset", use_container_width=True):
    p = PRESETS[preset_name]

    if p["prio_main"]:
        st.session_state["prio_race"] = p["prio_main"]["race"]
        st.session_state["prio_coin"] = p["prio_main"]["coin"]
        st.session_state["prio_drift"] = p["prio_main"]["drift"]
        st.session_state["prio_combat"] = p["prio_main"]["combat"]

    st.session_state["raw_selected"] = [x for x in p["raw_objective"] if x in KEY2IDX]
    for raw, lvl in (p["raw_priorities"] or {}).items():
        if raw in KEY2IDX:
            st.session_state[f"rawprio::{raw}"] = lvl

    st.session_state["preset_constraints_main"] = dict(p.get("constraints_main", {}) or {})
    st.session_state["preset_constraints_raw"] = dict(p.get("constraints_raw", {}) or {})

    st.rerun()

def prio_to_weight(label: str) -> float:
    return float(PRIORITY_MAP.get(label, 1.0))

def prio_weight_from_state(state_key: str, default_label: str = "Low") -> float:
    return prio_to_weight(st.session_state.get(state_key, default_label))

# Priority selectors (keyed so presets can set them)
st.sidebar.markdown("**Main priorities**")
st.sidebar.selectbox("Race priority", ["Low", "Medium", "High"], key="prio_race")
st.sidebar.selectbox("Coin priority", ["Low", "Medium", "High"], key="prio_coin")
st.sidebar.selectbox("Drift priority", ["Low", "Medium", "High"], key="prio_drift")
st.sidebar.selectbox("Combat priority", ["Low", "Medium", "High"], key="prio_combat")

w_race = prio_weight_from_state("prio_race", "Low")
w_coin = prio_weight_from_state("prio_coin", "Low")
w_drift = prio_weight_from_state("prio_drift", "Low")
w_combat = prio_weight_from_state("prio_combat", "Low")

# Raw priorities (optional)
st.sidebar.markdown("**Raw stat priorities (optional)**")
raw_choices = [
    "TrickSpd", "AirDriftTime", "DriftSteer", "Steer",
    "Speed", "StartBoost", "SlipStreamSpd",
    "StartCoins", "MaxCoins", "CoinBoostSpd", "CoinBoostTime",
    "UltCharge", "Daze", "SlipStreamRadius",
    "MaxCoinsSpd", "SlipTime", "UltStart", "DriftRate",
]
raw_choices = [x for x in raw_choices if x in KEY2IDX]

selected_raw = st.sidebar.multiselect(
    "Include these raw stats in objective",
    raw_choices,
    default=st.session_state.get("raw_selected", []),
    key="raw_selected",
    format_func=lambda x: RAW_UI_LABELS.get(x, x),
)

if "MaxCoins" in selected_raw:
    st.sidebar.caption("Note: **MaxCoins is minimised** (lower is better) when used in the objective.")

weights_raw = {}
for raw in selected_raw:
    level = st.sidebar.selectbox(
        f"{RAW_UI_LABELS.get(raw, raw)} priority",
        ["Low", "Medium", "High"],
        key=f"rawprio::{raw}",
    )
    weights_raw[raw] = prio_to_weight(level)

top_n = st.sidebar.slider("How many results?", 3, 5, 3, 1)

# Constraints
st.sidebar.markdown("---")
st.sidebar.header("3) Conditions")
enable_constraints = st.sidebar.checkbox("Enable constraints", value=True)

preset_constraints_main = dict(st.session_state.get("preset_constraints_main", {}) or {})
preset_constraints_raw = dict(st.session_state.get("preset_constraints_raw", {}) or {})
constraints_main = dict(preset_constraints_main)
constraints_raw = dict(preset_constraints_raw)

if enable_constraints:
    simple_above_zero = st.sidebar.checkbox("Simple: keep scores above zero", value=False)
    if simple_above_zero:
        constraints_main.update({k: (0.0, None) for k in MAIN_SCORES})

    from obk.ranges import estimate_main_score_ranges, estimate_raw_stat_ranges

    with st.sidebar.expander("Advanced constraints (min/max sliders)", expanded=False):
        dfE_all = df_from_category("ENGINE", stat_keys)
        dfX_all = df_from_category("EXHAUST", stat_keys)
        dfS_all = df_from_category("SUSPENSION", stat_keys)
        dfG_all = df_from_category("GEARBOX", stat_keys)
        dfT_all = df_from_category("TRINKET", stat_keys)

        dfE_sel = dfE_all[dfE_all["name"].isin(set(inventory["ENGINE"]))].reset_index(drop=True)
        dfX_sel = dfX_all[dfX_all["name"].isin(set(inventory["EXHAUST"]))].reset_index(drop=True)
        dfS_sel = dfS_all[dfS_all["name"].isin(set(inventory["SUSPENSION"]))].reset_index(drop=True)
        dfG_sel = dfG_all[dfG_all["name"].isin(set(inventory["GEARBOX"]))].reset_index(drop=True)
        dfT_sel = dfT_all[dfT_all["name"].isin(set(inventory["TRINKET"]))].reset_index(drop=True)

        if len(dfT_sel) < 2:
            st.warning("Need at least 2 trinkets selected to use advanced constraints.")
        else:
            ranges = estimate_main_score_ranges(dfE_sel, dfX_sel, dfS_sel, dfG_sel, dfT_sel)
            for k in MAIN_SCORES:
                lo, hi = ranges[k]
                step = float(max(0.1, (hi - lo) / 200.0))
                vmin, vmax = st.slider(
                    f"{k} allowed range",
                    min_value=float(lo),
                    max_value=float(hi),
                    value=(float(lo), float(hi)),
                    step=step,
                )
                if vmin > lo or vmax < hi:
                    constraints_main[k] = (float(vmin), float(vmax))

    with st.sidebar.expander("Raw stat constraints (min/max)", expanded=False):
        st.caption("Optional: enforce limits directly on raw totals (Speed, MaxCoins, etc.).")

        use_defaults = st.checkbox("Use sensible defaults", value=True)
        default_keys = list(RAW_CONSTRAINT_DEFAULTS.keys()) if use_defaults else []

        picked_raw = st.multiselect(
            "Stats to constrain",
            RAW_STAT_KEYS,
            default=sorted(set(default_keys + list(constraints_raw.keys()))),
            format_func=lambda x: RAW_UI_LABELS.get(x, x),
        )

        dfE_all = df_from_category("ENGINE", stat_keys)
        dfX_all = df_from_category("EXHAUST", stat_keys)
        dfS_all = df_from_category("SUSPENSION", stat_keys)
        dfG_all = df_from_category("GEARBOX", stat_keys)
        dfT_all = df_from_category("TRINKET", stat_keys)

        dfE_sel = dfE_all[dfE_all["name"].isin(set(inventory["ENGINE"]))].reset_index(drop=True)
        dfX_sel = dfX_all[dfX_all["name"].isin(set(inventory["EXHAUST"]))].reset_index(drop=True)
        dfS_sel = dfS_all[dfS_all["name"].isin(set(inventory["SUSPENSION"]))].reset_index(drop=True)
        dfG_sel = dfG_all[dfG_all["name"].isin(set(inventory["GEARBOX"]))].reset_index(drop=True)
        dfT_sel = dfT_all[dfT_all["name"].isin(set(inventory["TRINKET"]))].reset_index(drop=True)

        if len(dfT_sel) < 2:
            st.warning("Need at least 2 trinkets selected to use raw constraints.")
        else:
            ranges_raw = estimate_raw_stat_ranges(dfE_sel, dfX_sel, dfS_sel, dfG_sel, dfT_sel, picked_raw)

            for raw in picked_raw:
                lo, hi = ranges_raw.get(raw, (0.0, 0.0))
                step = float(max(0.05, (hi - lo) / 200.0)) if hi > lo else 0.05

                base_lo, base_hi = constraints_raw.get(raw, (None, None))
                if use_defaults and raw in RAW_CONSTRAINT_DEFAULTS:
                    d_lo, d_hi = RAW_CONSTRAINT_DEFAULTS[raw]
                    base_lo = d_lo if base_lo is None else base_lo
                    base_hi = d_hi if base_hi is None else base_hi

                v0 = float(lo if base_lo is None else base_lo)
                v1 = float(hi if base_hi is None else base_hi)

                vmin, vmax = st.slider(
                    f"{RAW_UI_LABELS.get(raw, raw)} allowed range",
                    min_value=float(lo),
                    max_value=float(hi),
                    value=(float(v0), float(v1)),
                    step=step,
                )

                if vmin > lo or vmax < hi:
                    constraints_raw[raw] = (float(vmin), float(vmax))

run = st.sidebar.button("Run optimiser", type="primary")

cfg = OptimiseConfig(
    top_n=int(top_n),
    weights_main={"race": w_race, "coin": w_coin, "drift": w_drift, "combat": w_combat},
    weights_raw=weights_raw,
    constraints_main=constraints_main,
    constraints_raw=constraints_raw,
    normalize_objective=bool(normalize_objective),
)

current_sig = make_run_signature(inventory, cfg)
last_sig = st.session_state.get("last_run_sig")
if last_sig is not None and current_sig != last_sig:
    st.warning("You changed parts/priorities/conditions since the last run. Click **Run optimiser** to refresh results.")

if run:
    for cat in CATEGORIES:
        if len(inventory[cat]) == 0:
            st.error(f"Select at least 1 item in {cat}.")
            st.stop()
    if len(inventory["TRINKET"]) < 2:
        st.error("Select at least 2 trinkets.")
        st.stop()

    try:
        df = optimise_builds(inventory, cfg)
    except Exception as e:
        st.error(str(e))
        st.stop()

    if df.empty:
        st.warning("No builds matched your constraints. Relax conditions or select more parts.")
        st.session_state["results_df"] = None
        st.session_state["last_run_sig"] = None
    else:
        show = normalize_scores_global(df)
        show["objective"] = show["objective"].round(4)
        st.session_state["results_df"] = show.reset_index(drop=True)
        st.session_state["last_run_sig"] = current_sig

with st.expander("Stat Legend / How Stats Work", expanded=False):
    st.markdown(LEGEND_HTML, unsafe_allow_html=True)

show = st.session_state.get("results_df")
if show is None or getattr(show, "empty", True):
    st.info("Select parts + set priorities/conditions, then click **Run optimiser**.")
else:
    st.subheader("Builds")
    st.caption("Scores are shown as 0–100 (% of theoretical maximum across all equipment). Hover a score for raw/max details.")
    render_build_table(show)
    render_compare_panel(show)

    st.download_button(
        "Download CSV",
        data=show.to_csv(index=False).encode("utf-8"),
        file_name="best_builds.csv",
        mime="text/csv",
        use_container_width=True,
    )
