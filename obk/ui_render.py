"""
UI rendering functions for the Build Optimiser app.
"""

import numpy as np
import streamlit as st
import textwrap
import streamlit.components.v1 as components

from .styles import APP_CSS
from .constants import STAT_SECTIONS, PERCENT_STATS
from .scoring import compute_global_score_maxima
from .ui_components import components_html_autosize, totals_for_build_row, render_stats_summary

def render_diff_header(show_df, idxs):
    base_i = idxs[0]
    st.markdown("##### Compared builds")

    cols = st.columns(len(idxs))
    for col, i in zip(cols, idxs):
        r = show_df.iloc[i]
        tag = "Baseline" if i == base_i else "Compared"

        col.markdown(
            f"**Build {i+1:02d} — {tag}**  \n"
            f"<span style='color: rgba(190,200,220,0.75); font-weight:800;'>"
            f"{r['ENGINE']} · {r['EXHAUST']} · {r['SUSPENSION']} · {r['GEARBOX']}<br/>"
            f"{r['TRINKET_1']} + {r['TRINKET_2']}"
            f"</span>",
            unsafe_allow_html=True,
        )

def render_visual_differences_grouped(show_df, idxs):
    idxs = [int(i) for i in idxs if 0 <= int(i) < len(show_df)]
    if len(idxs) < 2:
        st.info("Select at least 2 builds to see differences.")
        return

    base_i = idxs[0]
    comp_is = idxs[1:]
    n_comp = len(comp_is)

    base_stats = totals_for_build_row(show_df.iloc[base_i])
    comp_stats = {i: totals_for_build_row(show_df.iloc[i]) for i in comp_is}

    def esc(s):
        return (str(s)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))

    DIFF_CSS = f"""
    <style>
    .diff-card {{
        background:
            radial-gradient(1200px 450px at 15% 0%, rgba(16,54,51,0.16), rgba(0,0,0,0)),
            linear-gradient(180deg, rgba(7,10,10,0.92), rgba(5,7,7,0.92));
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 5px 5px rgba(0,0,0,0.35);
        font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
    }}

    /* Scroll container (vertical + horizontal) */
    .diff-scroll {{
        max-height: 70vh;
        overflow: auto;
        padding-right: 6px;
        scrollbar-gutter: stable;
        -webkit-overflow-scrolling: touch;
    }}

    /* Make sure grid doesn't squash too hard; triggers horizontal scroll when needed */
    .diff-table {{
        min-width: calc(170px + {n_comp} * 220px);
    }}

    .diff-head {{
        display: grid;
        grid-template-columns: 170px repeat({n_comp}, minmax(180px, 1fr));
        gap: 10px 12px;
        align-items: end;
        margin-bottom: 10px;
    }}
    .diff-colhead {{
        margin: 0;
        letter-spacing: 1.2px;
        font-size: 16px;
        font-weight: 700;
        color: rgba(255,255,255,0.92);
    }}

    .diff-section-title {{
        margin: 14px 0 6px 0;
        font-weight: 1000;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        font-size: 12px;
        color: rgba(190,200,220,0.72);
        display:flex;
        align-items:center;
        gap:8px;
    }}

    .diff-row {{
        display: grid;
        grid-template-columns: 170px repeat({n_comp}, minmax(180px, 1fr));
        gap: 10px 12px;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }}
    .diff-row:last-child{{ border-bottom: 0; }}

    .diff-stat {{
        font-weight: 1000;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        font-size: 11px;
        color: rgba(210,220,238,0.85);
    }}

    .diff-cell {{
        display:flex;
        flex-direction: column;
        gap: 4px;
    }}

    .delta-bar-wrap {{
        position: relative;
        height: 12px;
        background: rgba(255,255,255,0.08);
        border-radius: 999px;
        overflow: hidden;
    }}
    .delta-zero {{
        position: absolute;
        left: 50%;
        top: 0;
        bottom: 0;
        width: 1px;
        background: rgba(255,255,255,0.25);
    }}
    .delta-bar-pos {{
        position: absolute;
        left: 50%;
        height: 100%;
        background: linear-gradient(90deg, rgba(120,255,190,0.9), rgba(120,240,255,0.9));
    }}
    .delta-bar-neg {{
        position: absolute;
        right: 50%;
        height: 100%;
        background: linear-gradient(270deg, rgba(255,120,120,0.9), rgba(255,160,160,0.9));
    }}
    .delta-val {{
        font-size: 10px;
        font-weight: 900;
        letter-spacing: 0.2px;
        color: rgba(235,245,245,0.92);
    }}
    .delta-sub {{
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 0.6px;
        color: rgba(190,200,220,0.65);
        text-transform: uppercase;
    }}

    /*  =========================
        Themed + Autohide Scrollbar
        ========================= */

    /* Firefox: hide by default, show on hover */
    .diff-scroll {{
        scrollbar-width: thin;
        scrollbar-color: rgba(120,240,255,0.0) rgba(10,14,14,0.0);
    }}
    .diff-scroll:hover {{
        scrollbar-color: rgba(120,240,255,0.75) rgba(10,14,14,0.35);
    }}

    /* WebKit (Chrome/Edge/Safari) */
    .diff-scroll::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    .diff-scroll::-webkit-scrollbar-track {{
        background: rgba(10,14,14,0.35);
        border-radius: 999px;
    }}
    .diff-scroll::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, rgba(120,255,200,0.90), rgba(120,240,255,0.90));
        border-radius: 999px;
        border: 2px solid rgba(0,0,0,0.55);
        box-shadow: 0 0 8px rgba(120,240,255,0.35);
        opacity: 0; /* autohide default */
        transition: opacity 140ms ease;
    }}
    .diff-scroll:hover::-webkit-scrollbar-thumb {{
        opacity: 1;
    }}
    </style>
    """

    head = ["<div class='diff-head'>"]
    head.append("<div class='diff-colhead'>Stat</div>")
    for i in comp_is:
        head.append(f"<div class='diff-colhead'>Build {i+1:02d} Δ vs {base_i+1:02d}</div>")
    head.append("</div>")

    body = []
    body.append("<div class='diff-card'>")
    body.append("<div class='diff-scroll'><div class='diff-table'>")
    body.extend(head)

    for sec, icon, rows in STAT_SECTIONS:
        body.append(f"<div class='diff-section-title'>{esc(icon)}&nbsp; {esc(sec)}</div>")

        for stat, _cls in rows:
            base_val = float(base_stats.get(stat, 0.0))
            deltas = [float(comp_stats[i].get(stat, 0.0)) - base_val for i in comp_is]
            max_abs = max(1e-6, max(abs(d) for d in deltas))

            body.append("<div class='diff-row'>")
            body.append(f"<div class='diff-stat'>{esc(stat)}</div>")

            for d in deltas:
                width = min(50.0, (abs(d) / max_abs) * 50.0)
                bar = (
                    f"<div class='delta-bar-pos' style='width:{width:.2f}%;'></div>"
                    if d >= 0 else
                    f"<div class='delta-bar-neg' style='width:{width:.2f}%;'></div>"
                )

                suffix = "%" if stat in PERCENT_STATS else ""
                cell = f"""
                <div class="diff-cell">
                    <div class="delta-bar-wrap">
                        <div class="delta-zero"></div>
                        {bar}
                    </div>
                    <div class="delta-val">{d:+.2f}{suffix}</div>
                    <div class="delta-sub">baseline = 0</div>
                </div>
                """
                body.append(textwrap.dedent(cell).strip())

            body.append("</div>")

    body.append("</div></div>")  # close diff-table + diff-scroll
    body.append("</div>")        # close diff-card

    html = DIFF_CSS + "<div id='diff-root'>" + "".join(body) + "</div>"

    # Fixed iframe height; internal scroll handles overflow
    components_html_autosize(
        html,
        min_height=900,
        max_height=1700,
        key=f"diff-{base_i}-{'-'.join(map(str, comp_is))}"
    )

def render_build_table(df):
    selected = int(st.session_state.get("selected_build_idx", -1))
    show_stats = bool(st.session_state.get("show_stats", False))
    max_scores = compute_global_score_maxima()

    for i, r in df.iterrows():
        badge = str(i + 1).zfill(2)

        h1, h_cmp, h2 = st.columns([0.62, 0.18, 0.20], vertical_alignment="center")
        with h1:
            st.markdown(
                f'<div class="badge-wrap"><div class="build-badge">{badge}</div></div>',
                unsafe_allow_html=True
            )

        def on_compare_button(i, max_compare=3):
            idxs = list(st.session_state.get("compare_idxs", []))
            if i in idxs:
                idxs.remove(i)
                st.session_state["compare_warn"] = ""
            else:
                if len(idxs) >= max_compare:
                    st.session_state["compare_warn"] = f"You can compare up to {max_compare} builds."
                    return
                idxs.append(i)
                st.session_state["compare_warn"] = ""
            st.session_state["compare_idxs"] = sorted(set(idxs))

        with h_cmp:
            is_selected = (i in set(st.session_state.get("compare_idxs", [])))
            label = "Compare ✓" if is_selected else "Compare"
            if st.button(label, key=f"cmpbtn::{i}", use_container_width=True):
                on_compare_button(int(i), 3)
                st.rerun()

        with h2:
            is_open = (show_stats and selected == i)
            btn_label = "Hide details" if is_open else "View details"
            if st.button(btn_label, key=f"viewdetails::{i}", use_container_width=True):
                if is_open:
                    st.session_state["show_stats"] = False
                    st.session_state["selected_build_idx"] = -1
                else:
                    st.session_state["selected_build_idx"] = int(i)
                    st.session_state["show_stats"] = True
                st.rerun()

        def score_block(key, cls):
            vmax = float(max_scores.get(key, 0.0))
            raw = float(r.get(f"{key}_raw", r.get(key, 0.0)))
            pct = (raw / vmax * 100.0) if vmax > 0 else 0.0
            pct_clamped = float(np.clip(pct, 0.0, 100.0))
            width = pct_clamped

            tip = f"{pct:.1f}% of Max | Raw:{raw:.1f} | Max={vmax:.1f}"
            safe_tip = (
                    tip.replace("&", "&amp;")
                    .replace('"', "&quot;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
            )

            return f"""
            <div class="score-pill {cls}" data-tip="{safe_tip}">
                <div class="score-head">
                    <div class="score-name">{key.upper()}</div>
                    <div class="score-val">{pct_clamped:.0f}</div>
                </div>
                <div class="score-bar"><div style="width:{width:.2f}%"></div></div>
            </div>
            """

        row_html = f"""
        <div class="build-row">
            <div>
                <div class="parts-grid">
                    <div class="part-chip"><div class="part-label">ENGINE</div><div class="part-name">{r["ENGINE"]}</div></div>
                    <div class="part-chip"><div class="part-label">EXHAUST</div><div class="part-name">{r["EXHAUST"]}</div></div>
                    <div class="part-chip"><div class="part-label">SUSPENSION</div><div class="part-name">{r["SUSPENSION"]}</div></div>
                    <div class="part-chip"><div class="part-label">GEARBOX</div><div class="part-name">{r["GEARBOX"]}</div></div>
                    <div class="part-chip"><div class="part-label">TRINKET 1</div><div class="part-name">{r["TRINKET_1"]}</div></div>
                    <div class="part-chip"><div class="part-label">TRINKET 2</div><div class="part-name">{r["TRINKET_2"]}</div></div>
                </div>
            </div>
            <div class="score-grid">
                {score_block("race", "score-race")}
                {score_block("coin", "score-coin")}
                {score_block("drift", "score-drift")}
                {score_block("combat", "score-combat")}
            </div>
        </div>
        """

        components_html_autosize(APP_CSS + row_html, min_height=190, max_height=420, key=f"row-{i}")

        if show_stats and selected == i:
            stats = totals_for_build_row(r)
            render_stats_summary(stats)

def render_compare_panel(show_df):
    idxs = st.session_state.get("compare_idxs", [])
    idxs = [int(i) for i in idxs if 0 <= int(i) < len(show_df)]

    if st.session_state.get("compare_warn"):
        st.warning(st.session_state["compare_warn"])

    if len(idxs) < 2:
        return

    st.markdown("---")

    top = st.columns([0.7, 0.3], vertical_alignment="center")
    with top[0]:
        st.subheader("Compare Builds")
        st.caption("Pick 2-3 builds. Baseline is the first selected build.")
    with top[1]:
        if st.button("Clear comparison", use_container_width=True):
            st.session_state["compare_idxs"] = []
            st.session_state["compare_warn"] = ""
            st.rerun()

    render_diff_header(show_df, idxs)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    tabs = st.tabs(["Side-by-side", "Differences"])

    with tabs[0]:
        cols = st.columns(len(idxs))
        for col, i in zip(cols, idxs):
            r = show_df.iloc[i]
            with col:
                stats = totals_for_build_row(r)
                render_stats_summary(stats, badge_text=f"cmp-{i}")

    with tabs[1]:
        render_visual_differences_grouped(show_df, idxs)
