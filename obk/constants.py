"""
Constants for OBK optimiser.
"""

CATEGORIES = ["ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX", "TRINKET"]
MAIN_SCORES = ["race", "coin", "drift", "combat"]

RAW_STAT_KEYS = [
    "Speed", "StartBoost", "SlipStreamSpd", "SlowDownSpd",
    "StartCoins", "MaxCoins", "CoinBoostSpd", "CoinBoostTime",
    "DriftSteer", "Steer", "AirDriftTime",
    "UltCharge", "Daze", "SlipStreamRadius",
    "TrickSpd", "BoostPads", "MaxCoinsSpd", "SlipTime", "UltStart", "DriftRate",
    "T1", "T2", "T3",
]
RAW_STAT_KEYS = list(dict.fromkeys(RAW_STAT_KEYS))
KEY2IDX = {k: i for i, k in enumerate(RAW_STAT_KEYS)}

# COEFFS from compute_sensitivities.py
RACE_COEFFS = {'Speed': 2.899103582084764, 'SlipStreamSpd': 0.5645622655975568, 'StartBoost': 0.42906732185414326, 'SlowDownSpd': 0.10726683046353581}
COIN_COEFFS = {'CoinBoostTime': 2.112, 'StartCoins': 1.056, 'CoinBoostSpd': 0.352, 'MaxCoins': -0.48000000000000004}
DRIFT_COEFFS = {'AirDriftTime': 2.5301204724103483, 'Steer': 0.2530120572948303, 'DriftSteer': 0.21686747029482112}
COMBAT_COEFFS = {'UltCharge': 1.741935483870968, 'SlipStreamRadius': 0.7548387096774194, 'Daze': -0.503225806451613}

PRIORITY_MAP = {"Low": 1.0, "Medium": 2.5, "High": 5.0}

RAW_MINIMISE = {"MaxCoins"}  # used in UI hints

RAW_CONSTRAINT_DEFAULTS = {
    "Speed": (0.0, None),
    "MaxCoins": (None, 10.0),
}

PRESETS = {
    "Custom": {
        "prio_main": None,
        "raw_objective": [],
        "raw_priorities": {},
        "constraints_main": {},
        "constraints_raw": {},
    },
    "Race build": {
        "prio_main": {"race": "High", "coin": "Low", "drift": "Medium", "combat": "Low"},
        "raw_objective": ["Speed", "StartBoost", "SlipStreamSpd"],
        "raw_priorities": {"Speed": "High", "StartBoost": "Medium", "SlipStreamSpd": "Medium"},
        "constraints_main": {"race": (0.0, None)},
        "constraints_raw": {"Speed": (0.0, None)},
    },
    "Coin build": {
        "prio_main": {"race": "Low", "coin": "High", "drift": "Low", "combat": "Low"},
        "raw_objective": ["StartCoins", "MaxCoinsSpd", "CoinBoostSpd", "CoinBoostTime"],
        "raw_priorities": {"StartCoins": "High", "MaxCoinsSpd": "High", "CoinBoostSpd": "Medium", "CoinBoostTime": "Medium"},
        "constraints_main": {"coin": (0.0, None)},
        "constraints_raw": {"MaxCoins": (None, 10.0)},
    },
    "Handling build": {
        "prio_main": {"race": "Low", "coin": "Low", "drift": "High", "combat": "Low"},
        "raw_objective": ["Steer", "DriftSteer", "AirDriftTime"],
        "raw_priorities": {"Steer": "High", "DriftSteer": "High", "AirDriftTime": "Medium"},
        "constraints_main": {"drift": (0.0, None)},
        "constraints_raw": {},
    },
    "Trickjump build": {
        "prio_main": {"race": "Medium", "coin": "Low", "drift": "Medium", "combat": "Low"},
        "raw_objective": ["TrickSpd", "AirDriftTime", "DriftSteer"],
        "raw_priorities": {
            "TrickSpd": "High",
            "AirDriftTime": "Medium",
            "DriftSteer": "Medium",
        },
        "constraints_main": {},
        "constraints_raw": {"Speed": (0.0, None)},
    },
}

PERCENT_STATS = {"BoostPads", "SlowDownSpd", "DriftRate", "UltCharge", "Daze"}
STAT_SECTIONS = [
    ("Movement & Speed", "↗", [
        ("Speed", "c-blue"),
        ("StartBoost", "c-orange"),
        ("BoostPads", "c-yellow"),
        ("SlowDownSpd", "c-red"),
        ("TrickSpd", "c-blue"),
    ]),
    ("Handling & Drift", "〰", [
        ("Steer", "c-green"),
        ("DriftSteer", "c-purple"),
        ("DriftRate", "c-purple"),
        ("AirDriftTime", "c-blue"),
    ]),
    ("Coins & Economy", "◌", [
        ("StartCoins", "c-yellow"),
        ("MaxCoins", "c-orange"),
        ("MaxCoinsSpd", "c-orange"),
        ("CoinBoostSpd", "c-yellow"),
        ("CoinBoostTime", "c-yellow"),
    ]),
    ("Combat & Abilities", "⚔", [
        ("UltCharge", "c-pink"),
        ("UltStart", "c-pink"),
        ("Daze", "c-orange"),
        ("SlipStreamRadius", "c-purple"),
        ("SlipStreamSpd", "c-cyan"),
        ("SlipTime", "c-cyan"),
    ]),
    ("Drift Tiers Bonuses", "◎", [
        ("T1", "c-gray"),
        ("T2", "c-gray"),
        ("T3", "c-gray"),
    ]),
]

RAW_UI_LABELS = {
    "MaxCoins": "MaxCoins (lower is better)",
}
