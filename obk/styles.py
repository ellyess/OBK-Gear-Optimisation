"""
Styles for OBK Gear Optimiser Streamlit app.
Includes CSS styles and HTML snippets for UI components.
"""
LEGEND_CSS = r"""
<style>
/* Legend container */
.legend-wrap{
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 12px 14px;
    background: rgba(255,255,255,0.02);
}

/* Section headings */
.legend-h{
    font-weight: 1000;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin: 10px 0 6px 0;
    font-size: 12px;
    color: rgba(190,200,220,0.72);
}

/* Stat rows */
.legend-row{
    display:flex;
    align-items:flex-start;
    gap:10px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
.legend-row:last-child{ border-bottom: 0; }

.legend-key{
    min-width: 160px;
    font-weight: 1000;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    font-size: 12px;
    line-height: 1.2;
}
.legend-val{
    font-size: 12px;
    color: rgba(210,220,238,0.82);
    line-height: 1.35;
}

/* Reuse your existing color classes */
.legend-key.c-blue  { color: rgba(120,170,255,0.98); }
.legend-key.c-orange{ color: rgba(255,185,90,0.98); }
.legend-key.c-yellow{ color: rgba(255,215,90,0.98); }
.legend-key.c-red   { color: rgba(255,120,120,0.98); }
.legend-key.c-green { color: rgba(120,255,190,0.98); }
.legend-key.c-purple{ color: rgba(190,140,255,0.98); }
.legend-key.c-pink  { color: rgba(255,130,210,0.98); }
.legend-key.c-cyan  { color: rgba(120,240,255,0.98); }
.legend-key.c-gray  { color: rgba(190,200,220,0.85); }
</style>
"""

APP_CSS = r"""
<style>
:root{
    --accent:#103633;
    --text-main: rgba(235,245,245,0.95);
    --text-dim: rgba(190,200,220,0.85);
}

/* App background */
[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(1200px 700px at 18% 10%, rgba(16,54,51,0.22), rgba(0,0,0,0)),
        radial-gradient(900px 600px at 90% 0%, rgba(10,18,18,0.55), rgba(0,0,0,0)),
        linear-gradient(180deg, #050707 0%, #070b0b 45%, #050707 100%);
}
[data-testid="stHeader"]{ background: rgba(0,0,0,0); }

/* Sidebar */
[data-testid="stSidebar"]{
    background:
        radial-gradient(1000px 450px at 20% 0%, rgba(16,54,51,0.18), rgba(0,0,0,0)),
        linear-gradient(180deg, #060909 0%, #070d0d 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] div.block-container { padding-top: 1rem; }

/* Buttons */
.stButton>button{
    border-radius: 8px;
    border: 1px solid rgba(16,54,51,0.55);
    background: rgba(255,255,255,0.04);
    color: var(--text-main);
    font-weight: 1000;
    letter-spacing: 0.3px;
}
.stButton>button:hover{
    border-color: rgba(16,54,51,0.90);
    background: rgba(16,54,51,0.12);
}

/* ---- Chip containers (checkbox wrapper) ---- */
div[data-testid="stCheckbox"]{
    border-radius: 6px;
    border: 1px solid rgba(16,54,51,0.55);
    background: rgba(255,255,255,0.03);
    padding: 0.18rem 0.55rem;
    margin: 0.10rem 0;
    transition: all 120ms ease;
}
div[data-testid="stCheckbox"]:hover{
    border-color: rgba(16,54,51,0.90);
    background: rgba(16,54,51,0.12);
}
div[data-testid="stCheckbox"] label{
    cursor: pointer;
    color: rgba(210,220,238,0.86);
    font-weight: 900;
    letter-spacing: 0.2px;
}

/* Highlight covers the WHOLE chip border */
div[data-testid="stCheckbox"]:has(input:checked){
    border-color: rgba(16,54,51,0.95) !important;
    background: rgba(16,54,51,0.22) !important;
    box-shadow: 0 0 0 3px rgba(16,54,51,0.25) !important;
}
div[data-testid="stCheckbox"] input:checked + div{
    background: transparent !important;
    outline: none !important;
    box-shadow: none !important;
}
div[data-testid="stCheckbox"]:has(input:checked) label{
    color: rgba(235,255,252,0.95) !important;
}

/* Sliders: remove “background card” feel */
div[data-testid="stSlider"]{
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    padding: 0.1rem 0 0.2rem 0 !important;
}
div[data-testid="stSlider"] > div{
    background: transparent !important;
}

/* ---- Results Table (cards) ---- */
.results-wrap{
    display:flex;
    flex-direction:column;
    gap:10px;
}

/* Ensure consistent font */
.build-row, .build-row *{
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial !important;
}

.build-row{
    display:grid;
    grid-template-columns: 1.65fr 0.95fr;
    gap:10px;
    padding:9px 10px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.10);
    background:
        radial-gradient(1200px 450px at 15% 0%, rgba(16,54,51,0.16), rgba(0,0,0,0)),
        linear-gradient(180deg, rgba(7,10,10,0.92), rgba(5,7,7,0.92));
    box-shadow: 0 5px 5px rgba(0,0,0,0.35);
}
.parts-grid{
    display:grid;
    grid-template-columns: 1fr 1fr;
    gap:7px 9px;
}
.part-chip{
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.03);
    padding: 7px 9px;
}
.part-label{
    font-size:10px;
    letter-spacing:1px;
    text-transform:uppercase;
    color: rgba(190,200,220,0.65);
    font-weight:1000;
    margin-bottom:4px;
}
.part-name{
    font-size:12px;
    font-weight:1000;
    letter-spacing:0.2px;
    color: rgba(235,245,245,0.95);
}

/* scores in a 2x2 grid */
.score-grid{
    display:grid;
    grid-template-columns: repeat(2, 1fr);
    gap:7px 9px;
    align-content:center;
}
.score-pill{
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.10);
    background: rgba(255,255,255,0.03);
    padding: 7px 9px;
    box-shadow: 0 5px 5px rgba(0,0,0,0.35);
}
.score-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:15px;
}
.score-name{
    font-size:10px;
    font-weight:1000;
    letter-spacing:1.2px;
}
.score-val{
    font-size:10px;
    font-weight:1000;
    color: rgba(235,245,245,0.92);
}

/* bar */
.score-bar{
    height:10px;
    width:100%;
    border-radius:999px;
    background: rgba(255,255,255,0.08);
    overflow:hidden;
}
.score-bar > div{
    height:100%;
    width: 0%;
    border-radius:999px;
    background: rgba(235,245,245,0.90);
}

/* Tooltip */
.score-pill{ position: relative; }

.score-pill[data-tip]:hover::after,
.score-pill[data-tip]:hover::before{
    z-index: 9999;
}

/* IMPORTANT: tooltip draws INSIDE the pill, so no clipping issues */
.score-pill[data-tip]:hover::after{
    content: attr(data-tip);
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    padding: 7px 9px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(10,12,12,0.95);
    color: rgba(235,245,245,0.95);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.2px;
    box-shadow: 0 5px 5px rgba(0,0,0,0.35);
    pointer-events: none;
    white-space: normal;
}

/* label colors */
.score-race .score-name{ color: rgba(120,170,255,0.98); }
.score-coin .score-name{ color: rgba(255,215,90,0.98); }
.score-drift .score-name{ color: rgba(190,140,255,0.98); }
.score-combat .score-name{ color: rgba(255,120,120,0.98); }

/* badge + row header */
.build-badge{
    display:inline-grid;
    place-items:center;
    width: 34px; height: 34px;
    border-radius: 8px;
    border: 1px solid rgba(16,54,51,0.65);
    background: rgba(16,54,51,0.25);
    color: rgba(185,255,245,0.92);
    font-weight:900;
    font-size:16px;
}
.row-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin: 0px 0 6px 0;
}
.row-head .title{
    display:flex;
    align-items:center;
    gap:10px;
    color: rgba(235,245,245,0.95);
    font-weight:1000;
    letter-spacing:0.5px;
}
.row-head .hint{
    color: rgba(190,200,220,0.65);
    font-size:12px;
    font-weight:800;
}

/* --- Header row: badge + button alignment (no guessing parent heights) --- */
div[data-testid="column"]:has(.badge-wrap){
  display: flex !important;
  align-items: center !important;
}
div[data-testid="column"]:has(.badge-wrap) .stMarkdown,
div[data-testid="column"]:has(.badge-wrap) .stMarkdown > div{
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="column"]:has(button[key^="viewdetails"]) {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
}
div[data-testid="column"]:has(.badge-wrap) + div[data-testid="column"]{
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
}
.badge-wrap{ transform: translateY(2px); }
</style>
"""


STATS_PANEL_CSS = """
<style>
.stats-card {
    background:
        radial-gradient(1200px 450px at 15% 0%, rgba(16,54,51,0.16), rgba(0,0,0,0)),
        linear-gradient(180deg, rgba(7,10,10,0.92), rgba(5,7,7,0.92));
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 8px;
    padding: 14px 18px 14px 18px;
    box-shadow: 0 5px 5px rgba(0,0,0,0.35);
    font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
.stats-title {
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.10);
    margin-bottom: 10px;
}
.stats-title h3 {
    margin: 0;
    letter-spacing: 1.2px;
    font-size: 16px;
    font-weight: 700;
    color: rgba(255,255,255,0.92);
}
.stats-section { margin-top: 14px; }
.stats-section-h {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 900;
    letter-spacing: 0.9px;
    font-size: 12px;
    color: rgba(185,195,215,0.70);
    text-transform: uppercase;
    margin-bottom: 6px;
}
.stats-hr { height: 1px; background: rgba(255,255,255,0.07); margin: 8px 0 2px 0; }
.stats-row { display: flex; justify-content: space-between; padding: 4px 0; }
.stats-key {
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.8px;
    color: rgba(210,220,238,0.78);
    text-transform: uppercase;
}
.stats-val { font-size: 12px; font-weight: 900; letter-spacing: 0.6px; }

.c-blue  { color: rgba(120,170,255,0.98); }
.c-orange{ color: rgba(255,185,90,0.98); }
.c-yellow{ color: rgba(255,215,90,0.98); }
.c-red   { color: rgba(255,120,120,0.98); }
.c-green { color: rgba(120,255,190,0.98); }
.c-purple{ color: rgba(190,140,255,0.98); }
.c-pink  { color: rgba(255,130,210,0.98); }
.c-cyan  { color: rgba(120,240,255,0.98); }
.c-gray  { color: rgba(190,200,220,0.85); }
</style>
"""

LEGEND_HTML = r"""
<div class="legend-wrap">
<div class="legend-h">Movement & Speed</div>
<div class="legend-row">
    <div class="legend-key c-blue">Speed</div>
    <div class="legend-val">Base speed increase.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-yellow">Boost Pads</div>
    <div class="legend-val">Modifies the amount of speed boost pads give you.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-orange">Start Boost</div>
    <div class="legend-val">Change in speed when successfully getting a start boost.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-cyan">SlipStream Spd</div>
    <div class="legend-val">Extra speed while slipstreaming.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-purple">SlipStream Radius</div>
    <div class="legend-val">Change in radius to detect a target to slipstream.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-cyan">SlipStream Time</div>
    <div class="legend-val">Change in duration of slipstream boosts.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-red">SlowDownSpd</div>
    <div class="legend-val">Speed modifier in slowdown areas (puddles, etc.). Higher is faster.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-blue">Trick Spd</div>
    <div class="legend-val">Modifies the amount of speed while under the effect of a trickjump boost.</div>
</div>

<div class="legend-h">Handling & Drift</div>
<div class="legend-row">
    <div class="legend-key c-purple">Drift Rate</div>
    <div class="legend-val">The rate at which your drift bar fills when drifting. Higher is faster.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-purple">Drift Steer</div>
    <div class="legend-val">Change in handling force while drifting.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-green">Steer</div>
    <div class="legend-val">Change in handling force while NOT drifting.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-blue">AirDrift Time</div>
    <div class="legend-val">Modifies the duration that you can maintain a drift while in the air (seconds).</div>
</div>
<div class="legend-h">Coins & Economy</div>
<div class="legend-row">
    <div class="legend-key c-yellow">Start Coins</div>
    <div class="legend-val">Change in amount of coins you start the race with.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-orange">MaxCoins</div>
    <div class="legend-val">Amount of coins needed to get coin boost and max coin speed. <b>Lower is better.</b></div>
</div>
<div class="legend-row">
    <div class="legend-key c-orange">MaxCoins Spd</div>
    <div class="legend-val">Change in amount of speed on max coins (not CoinBoost Spd).</div>
</div>
<div class="legend-row">
    <div class="legend-key c-yellow">CoinBoost Spd</div>
    <div class="legend-val">Modifies the temporary speed boost on hitting max coins.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-yellow">CoinBoost Time</div>
    <div class="legend-val">Modifies the duration of the speed boost on hitting max coins.</div>
</div>
<div class="legend-h">Combat & Abilities</div>
<div class="legend-row">
    <div class="legend-key c-pink">UltCharge</div>
    <div class="legend-val">Changes the rate at which your ultimate bar fills.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-pink">UltStart</div>
    <div class="legend-val">Changes the amount of ultimate charge you start a race with (flat amount).</div>
</div>
<div class="legend-row">
    <div class="legend-key c-orange">Daze</div>
    <div class="legend-val">% change to how long you stay dazed. Higher = longer (worse).</div>
</div>
<div class="legend-h">Drift Tier Bonuses</div>
<div class="legend-row">
    <div class="legend-key c-gray">T1</div>
    <div class="legend-val">Amount of speed added on a tier 1 drift ignition.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-gray">T2</div>
    <div class="legend-val">Amount of speed added on a tier 2 drift ignition.</div>
</div>
<div class="legend-row">
    <div class="legend-key c-gray">T3</div>
    <div class="legend-val">Amount of speed added on a tier 3 drift ignition.</div>
</div>
<div class="legend-h">How scoring works</div>
<div class="legend-row">
    <div class="legend-key c-gray">Scores (0–100)</div>
    <div class="legend-val">
    Each build’s <b>Race/Coin/Drift/Combat</b> is shown as <b>% of theoretical maximum</b> across all equipment
    (100% = best possible build using the full database).
    </div>
</div>
</div>
"""