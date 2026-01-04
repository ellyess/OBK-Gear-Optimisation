"""
UI components for OBK Gear Optimiser.
Includes functions for rendering stats summaries and autosizing HTML components.
"""

import uuid
import textwrap
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

from .constants import RAW_STAT_KEYS, KEY2IDX, STAT_SECTIONS, PERCENT_STATS
from .data import df_from_category
from .styles import STATS_PANEL_CSS

def components_html_autosize(html, *, min_height=50, max_height=2000, key=None):
    if key is None:
        key = str(uuid.uuid4())

    wrapper_id = f"autosize-{key}"

    rendered = f"""
    <div id="{wrapper_id}">{html}</div>

    <script>
    (function() {{
        const MIN_H = {int(min_height)};
        const MAX_H = {int(max_height)};

        function clamp(x) {{
            return Math.max(MIN_H, Math.min(MAX_H, x));
        }}

        function getHeight() {{
            const body = document.body;
            const html = document.documentElement;
            const h = Math.max(
                body.scrollHeight, body.offsetHeight,
                html.clientHeight, html.scrollHeight, html.offsetHeight
            );
            return clamp(h + 4);
        }}

        function postHeight() {{
            const height = getHeight();
            window.parent.postMessage(
                {{
                    isStreamlitMessage: true,
                    type: "streamlit:setFrameHeight",
                    height: height
                }},
                "*"
            );
        }}

        window.addEventListener("load", postHeight);
        window.addEventListener("resize", () => {{
            requestAnimationFrame(postHeight);
        }});

        const target = document.getElementById("{wrapper_id}") || document.body;

        if ("ResizeObserver" in window) {{
            const ro = new ResizeObserver(() => requestAnimationFrame(postHeight));
            ro.observe(target);
        }}

        if ("MutationObserver" in window) {{
            const mo = new MutationObserver(() => requestAnimationFrame(postHeight));
            mo.observe(target, {{ childList: true, subtree: true, attributes: true, characterData: true }});
        }}

        setTimeout(postHeight, 50);
        setTimeout(postHeight, 250);
    }})();
    </script>
    """
    components.html(rendered, height=min_height, scrolling=False)

def _part_vec(cat, name):
    stat_keys = tuple(RAW_STAT_KEYS)
    df = df_from_category(cat, stat_keys)
    r = df[df["name"] == name]
    if r.empty:
        return np.zeros(len(RAW_STAT_KEYS), dtype=np.float32)
    return r[RAW_STAT_KEYS].to_numpy(np.float32)[0]

def totals_for_build_row(row):
    v = (
        _part_vec("ENGINE", row["ENGINE"])
        + _part_vec("EXHAUST", row["EXHAUST"])
        + _part_vec("SUSPENSION", row["SUSPENSION"])
        + _part_vec("GEARBOX", row["GEARBOX"])
        + _part_vec("TRINKET", row["TRINKET_1"])
        + _part_vec("TRINKET", row["TRINKET_2"])
    )
    return {k: float(v[KEY2IDX[k]]) for k in RAW_STAT_KEYS}

def render_stats_summary(stats, badge_text="01"):
    def fmt(k, v):
        return f"{v:.2f}%" if k in PERCENT_STATS else f"{v:.2f}"

    parts = []
    parts.append('<div class="stats-card">')
    parts.append(
        """
        <div class="stats-title">
            <h3>Stat Summary</h3>
        </div>
        """
    )
    for si, (sec, icon, rows) in enumerate(STAT_SECTIONS):
        parts.append(f'<div class="stats-section"><div class="stats-section-h">{icon}&nbsp; {sec}</div>')
        for k, cls in rows:
            v = float(stats.get(k, 0.0))
            parts.append(
                f"""
                <div class="stats-row">
                    <div class="stats-key">{k}</div>
                    <div class="stats-val {cls}">{fmt(k, v)}</div>
                </div>
                """
            )
        parts.append("</div>")
        if si != len(STAT_SECTIONS) - 1:
            parts.append('<div class="stats-hr"></div>')
    parts.append("</div>")

    html = STATS_PANEL_CSS + "".join(parts)
    components_html_autosize(html, min_height=790, max_height=900, key=f"stats-{badge_text}")
