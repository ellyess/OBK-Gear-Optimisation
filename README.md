# OBK Gear Optimiser

**OBK Gear Optimiser** is a data-driven Streamlit application for exploring and optimising gear builds in **Oh Baby Kart (OBK)**. It helps you find the best possible builds from your owned equipment based on **playstyle priorities**, **stat constraints**, and **objective weighting**.


---

## Features

- Select owned parts across all categories (Engine, Exhaust, Suspension, Gearbox, Trinkets)

- Optimise builds using weighted **Race / Coin / Drift / Combat** scores

- Add **raw stat objectives** (Speed, TrickSpd, AirDriftTime, etc.)

- Enforce **hard constraints** on scores *and* raw stats

- Built-in presets (Race, Coin, Handling, Trickjump)

- Optional **normalisation toggle** for fair multi-stat optimisation

- Compare up to **3 builds side-by-side** with visual stat deltas

- Export results as CSV

---

## Installation

### 1. Create the environment

```bash
conda env create -f environment.yaml
conda activate OBK-gear
```

### 2. Run the app

```bash
streamlit run app.py
```

---

## Project Structure

```text
.
├── app.py                     # Streamlit entry point
├── environment.yaml
├── README.md
└── obk/
    ├── __init__.py
    ├── constants.py           # Stats, coefficients, presets
    ├── data.py                # PARTS_DATABASE
    ├── scoring.py             # Score computation + normalisation
    ├── optimiser.py           # Build optimisation logic
    ├── ranges.py              # Stat range estimation
    ├── legend.py              # Legend HTML
    ├── styles.py              # APP CSS
    ├── ui_state.py            # Session state + inventory handling
    ├── ui_components.py       # Rendering + autosizing HTML
    └── ui_render.py           # Tables, stats panels, comparisons
    
```

---

## Optimisation Method (Overview)

### 1. Build Enumeration

For the selected inventory, the optimiser evaluates all valid combinations of:

```text
ENGINE × EXHAUST × SUSPENSION × GEARBOX × (2 distinct TRINKETS)
```

Duplicate trinkets are automatically excluded.

---

### 2. Raw Stat Aggregation

Each build produces a vector of raw stats (e.g. Speed, StartBoost, MaxCoins, TrickSpd, Daze).
Stats are summed across all selected parts.

---

### 3. Main Score Calculation

Four main scores are computed as **linear combinations** of raw stats:

- **Race**

- **Coin**

- **Drift**

- **Combat**

Each score uses a coefficient dictionary:

```python
RACE_COEFFS   = {stat: weight, ...}
COIN_COEFFS   = {stat: weight, ...}
DRIFT_COEFFS  = {stat: weight, ...}
COMBAT_COEFFS = {stat: weight, ...}
```

The **sign of the coefficient encodes direction**:

- Positive → higher is better

- Negative → lower is better (e.g. MaxCoins, Daze)

No special-case logic is required elsewhere.

---

### 4. Optional Normalisation (Recommended)

When **Normalise stats** is enabled:

- Scores and raw stats in the objective are scaled to **0–1**

- Ranges are computed from the **currently selected inventory**

- This prevents mixed-unit stats (seconds, %, flat values) from dominating

When disabled:

- Raw values are used directly

- Large-range stats may dominate the objective

This toggle allows easy **A/B testing**.

---

### 5. Objective Function

The optimiser maximises:

```text
Objective =
Σ (main_score_weight × main_score)
+ Σ (raw_stat_weight × raw_stat)
```

Weights come from **Low / Medium / High** priorities.
Raw stats that are “lower is better” are automatically inverted.

---

### 6. Constraints

Constraints filter builds **before ranking**.

Supported constraints:

- **Main score constraints** (e.g. Race ≥ 0)

- **Raw stat constraints** (e.g. MaxCoins ≤ 10, Speed ≥ 0)

Every returned build satisfies all active constraints.

---

### 7. Ranking & Results

- Builds are ranked by final objective value

- Duplicate builds are removed

- Top-N results are displayed with score breakdowns

- Scores are shown as **0–100 (% of theoretical maximum)** across the full database

---

## Coefficient Tuning (Advanced)

Coefficients can be retuned using the provided Monte Carlo sensitivity script:

```bash
python compute_sensitivities.py
```

This script:

- Samples hundreds of thousands of random builds

- Computes robust P90–P10 stat ranges

- Produces **unit-balanced coefficients** so each stat contributes comparably

This makes balance **data-driven rather than guess-based**.

---

## License

MIT License

```text
Copyright (c) 2025–2026 Ellyess
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```
