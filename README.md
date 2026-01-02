# OBK Gear Optimiser
A visual build optimiser for OBK setups, available online <https://obk-gear-optimiser.streamlit.app/>. Scoring and statistics based on <https://tarawoy.github.io/OBKGear/>.

Designed to explore optimal combinations of parts based on player priorities, constraints, and owned equipment.

## Features
- **Part-based optimisation**
  - Engine, Exhaust, Suspension, Gearbox, Trinkets
- **Priority-based scoring**
  - Race
  - Coin
  - Drift
  - Combat
- **Optional raw stat weighting**
- **Constraint system**
  - Simple: keep scores above zero
  - Advanced: min/max sliders per score
- **Interactive results**
  - Ranked build list
  - Expandable per-build stat breakdown
- **CSV export**
---

## How It Works
Each build is composed of:
- 1 × Engine  
- 1 × Exhaust  
- 1 × Suspension  
- 1 × Gearbox  
- 2 × Trinkets (no duplicates)

Every possible combination is evaluated using weighted scoring formulas.

### Main Scores
| Score | Based on |
|------|---------|
| Race | Speed, boost, slipstream |
| Coin | Coins gained & coin efficiency |
| Drift | Steering & air control |
| Combat | Daze, ult charge, disruption |

You control how important each category is using **Low / Medium / High** priorities.

---

## Usage

```bash
conda env create -f environment.yaml
conda activate OBK-gear
streamlit run app.py
```

## Method

```python
objective = w1 * race + w2 * coin + w3 * drift + w4 * combat + raw_weights
```