"""
UI state management for OBK Gear Optimiser.
Includes functions for initialising and updating session state.
"""

import re
import streamlit as st

from .constants import CATEGORIES, RAW_STAT_KEYS, MAIN_SCORES

def init_owned_state(names_by_cat):
    if "owned" not in st.session_state:
        st.session_state["owned"] = {cat: {nm: False for nm in names_by_cat[cat]} for cat in CATEGORIES}
    else:
        owned = st.session_state["owned"]
        for cat in CATEGORIES:
            owned.setdefault(cat, {})
            for nm in names_by_cat[cat]:
                owned[cat].setdefault(nm, False)

    st.session_state.setdefault("chip_version", 0)
    st.session_state.setdefault("selected_build_idx", -1)
    st.session_state.setdefault("show_stats", False)
    st.session_state.setdefault("results_df", None)
    st.session_state.setdefault("last_run_sig", None)
    st.session_state.setdefault("import_text", "")
    st.session_state.setdefault("compare_idxs", [])
    st.session_state.setdefault("compare_warn", "")

    st.session_state.setdefault("preset_name", "Custom")
    st.session_state.setdefault("preset_constraints_main", {})
    st.session_state.setdefault("preset_constraints_raw", {})
    st.session_state.setdefault("raw_selected", [])

def set_all_owned(value, names_by_cat):
    owned = st.session_state["owned"]
    for cat, names in names_by_cat.items():
        for nm in names:
            owned[cat][nm] = bool(value)
    st.session_state["chip_version"] += 1

def on_chip_change(cat, nm, widget_key):
    st.session_state["owned"][cat][nm] = bool(st.session_state[widget_key])

def part_toggle_grid(cat, names):
    import streamlit as st
    
    st.sidebar.subheader(cat.title())
    cols = st.sidebar.columns(2)
    selected = []
    owned = st.session_state["owned"][cat]
    v = int(st.session_state.get("chip_version", 0))

    for i, nm in enumerate(sorted(names, key=lambda x: x.lower())):
        col = cols[i % len(cols)]
        widget_key = f"chip::{cat}::{nm}::v{v}"
        with col:
            st.checkbox(
                nm,
                value=bool(owned.get(nm, False)),
                key=widget_key,
                on_change=on_chip_change,
                args=(cat, nm, widget_key),
            )
        if bool(owned.get(nm, False)):
            selected.append(nm)

    if cat == "TRINKET" and len(selected) < 2:
        st.sidebar.warning("Pick at least 2 trinkets (duplicates are automatically avoided).")
    return selected

def build_name_lookup(names_by_cat):
    lookup = {}
    ambiguous = set()
    for cat, names in names_by_cat.items():
        for nm in names:
            key = nm.strip().lower()
            if key in lookup and lookup[key][0] != cat:
                ambiguous.add(key)
            else:
                lookup[key] = (cat, nm)
    for k in ambiguous:
        lookup[k] = ("AMBIGUOUS", lookup[k][1])
    return lookup, ambiguous

def parse_import_text(text):
    if not text or not text.strip():
        return []
    parts = re.split(r"[\n,;]+", text)
    return [p.strip() for p in parts if p.strip()]

def apply_import_replace(text, names_by_cat):
    tokens = parse_import_text(text)
    lookup, _ambiguous = build_name_lookup(names_by_cat)

    owned = st.session_state["owned"]
    for cat in CATEGORIES:
        for nm in names_by_cat[cat]:
            owned[cat][nm] = False

    unknown, amb = [], []
    applied = 0

    for t in tokens:
        key = t.lower()
        if key not in lookup:
            unknown.append(t)
            continue
        cat, nm = lookup[key]
        if cat == "AMBIGUOUS":
            amb.append(t)
            continue
        owned[cat][nm] = True
        applied += 1

    st.session_state["chip_version"] += 1
    return applied, unknown, amb

def make_run_signature(inventory, cfg):
    inv_sig = tuple((cat, tuple(sorted(inventory.get(cat, [])))) for cat in CATEGORIES)
    w_main_sig = tuple(sorted(cfg.weights_main.items()))
    w_raw_sig = tuple(sorted(cfg.weights_raw.items()))
    c_main_sig = tuple(sorted((k, cfg.constraints_main.get(k, (None, None))) for k in MAIN_SCORES))
    c_raw_sig = tuple(sorted((k, cfg.constraints_raw.get(k, (None, None))) for k in RAW_STAT_KEYS))
    preset_sig = str(st.session_state.get("preset_name", "Custom"))
    norm_sig = bool(getattr(cfg, "normalize_objective", True))
    return (inv_sig, w_main_sig, w_raw_sig, c_main_sig, c_raw_sig, preset_sig, int(cfg.top_n), norm_sig)
