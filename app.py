"""
Application: OBK Gear Optimiser
Author: Ellyess
Date: 2025-12-30
Description:
    A Streamlit app to optimise OBK gear builds (including Characters) based on user-defined priorities and constraints.

IMPORTANT CHANGE (Character = Baseline):
    - Characters are stored as ABSOLUTE baseline stats (not baseline-subtracted deltas).
    - Optimiser *scores and optimises using GEAR GAIN only*:
          gear_gain = (character + gear) - character
    - The build detail panel shows BOTH:
          1) Gear Gain (what equipment adds)
          2) Absolute (character + equipment)

Run:
    conda env create -f environment.yaml
    conda activate kart-optimiser
    streamlit run app.py
"""

import re
import uuid
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# 1) PARTS DATABASE
# =========================================================
PARTS_DATABASE = {
    "ENGINE": [
        {"name": "Advanced Engine", "stats": {"T3": 1, "DriftSteer": 1, "Steer": 1, "AirDriftTime": 0.2, "Speed": 1, "SlipStreamRadius": 20, "SlipStreamSpd": 3.5}},
        {"name": "Banker Engine", "stats": {"BoostPads": 10, "T2": -0.5, "StartBoost": -5, "StartCoins": 3, "MaxCoins": 10, "MaxCoinsSpd": 2, "DriftSteer": -2, "Steer": -2, "Speed": -0.2}},
        {"name": "Basic Engine", "stats": {"Speed": 0.5}},
        {"name": "Scrapwork Engine", "stats": {"T1": -0.8, "T2": -1, "T3": 0.5, "DriftSteer": -5, "Steer": -4, "Speed": 1.6, "SlipStreamRadius": 35, "SlipStreamSpd": 2}},
        {"name": "Chrome Engine", "stats": {"T3": 1.6, "StartBoost": 10, "Speed": 0.5}},
        {"name": "Clean Engine", "stats": {"T1": 0.4, "T2": 0.5, "DriftSteer": 0.5, "Steer": 0.5, "SlipStreamRadius": 100, "TrickSpd": 5}},
        {"name": "Cyber Engine", "stats": {"T3": 1.2, "DriftSteer": 0.5, "Steer": 0.5, "Speed": 0.5, "SlipStreamSpd": 5}},
        {"name": "Featherweight Engine", "stats": {"T1": 0.8, "DriftSteer": 1, "Steer": 1, "AirDriftTime": 0.2, "Speed": 0.3, "Daze": -12, "SlipStreamRadius": 30, "TrickSpd": 5}},
        {"name": "Fresh Engine", "stats": {"BoostPads": 4, "MaxCoinsSpd": 0.2, "Speed": 0.3, "TrickSpd": 3.2}},
        {"name": "Frontrunner Engine", "stats": {"T3": 1, "StartBoost": 15, "CoinBoostSpd": 10, "CoinBoostTime": 0.5, "StartCoins": 1, "MaxCoins": -1, "MaxCoinsSpd": 1.4, "Speed": -0.2}},
        {"name": "Spooky Engine", "stats": {"T1": 0.6, "StartBoost": 10, "Speed": 0.6, "TrickSpd": 3}},
        {"name": "Heavyweight Engine", "stats": {"CoinBoostSpd": 5, "CoinBoostTime": 0.5, "StartCoins": 2, "MaxCoins": 5, "MaxCoinsSpd": 0.8, "DriftSteer": -4.5, "Steer": -3.5, "Speed": 1.3, "Daze": 50, "TrickSpd": -3}},
        {"name": "Vulcan Engine", "stats": {"DriftRate": 2.5, "T3": 1, "MaxCoins": -1, "MaxCoinsSpd": 0.5, "DriftSteer": -0.5, "Steer": -2, "Speed": 0.5, "Daze": 100}},
        {"name": "No Coiner Engine", "stats": {"T2": 1.5, "T3": 1, "CoinBoostSpd": -10, "MaxCoins": -2, "MaxCoinsSpd": -5.2, "Speed": 3.2, "TrickSpd": 4}},
        {"name": "Piggybank Engine", "stats": {"StartCoins": 2, "MaxCoins": 10, "MaxCoinsSpd": 4.5, "Speed": -2.7}},
        {"name": "Scrap Engine", "stats": {"T1": 0.4, "T2": 0.5, "T3": 0.5, "TrickSpd": 3.5}},
        {"name": "Silver Engine", "stats": {"T1": 0.5, "T2": 0.7, "T3": 1.4}},
        {"name": "Snail Engine", "stats": {"BoostPads": 10, "Speed": -2.5, "SlowAreaPenalty": 50, "Daze": -30, "UltCharge": 8, "UltStart": 18, "SlipStreamRadius": 30, "SlipStreamSpd": 7, "SlipTime": 0.8}},
        {"name": "Starter Engine", "stats": {"T1": 0.8, "CoinBoostTime": 1, "MaxCoinsSpd": 0.6, "Speed": 0.6}},
    ],
    "EXHAUST": [
        {"name": "Acrobatic Exhaust", "stats": {"CoinBoostTime": 1, "DriftSteer": 1.2, "Steer": 1.2, "AirDriftTime": 0.13, "TrickSpd": 2}},
        {"name": "Ice Exhaust", "stats": {"CoinBoostSpd": 5, "CoinBoostTime": 0.6, "Speed": 0.5, "T1": 0.8, "T3": 1}},
        {"name": "Discharged Exhaust", "stats": {"Speed": 1.6, "UltCharge": -20, "UltStart": 10, "TrickSpd": 2.5}},
        {"name": "Cyber Exhaust", "stats": {"UltStart": 17, "TrickSpd": 3.5}},
        {"name": "Iron Exhaust", "stats": {"StartBoost": 10, "CoinBoostSpd": -5, "CoinBoostTime": 2.5, "UltCharge": 5, "SlipStreamRadius": 25, "SlipTime": 1.2, "BoostPads": 5, "SlipStreamSpd": 3.5}},
        {"name": "Light Exhaust", "stats": {"CoinBoostTime": 1, "MaxCoinsSpd": 0.2, "AirDriftTime": 0.15, "UltStart": 10, "SlipStreamRadius": 15, "SlipStreamSpd": 3, "TrickSpd": 5}},
        {"name": "Fresh Exhaust", "stats": {"CoinBoostSpd": 5, "CoinBoostTime": 0.3, "DriftSteer": 0.2, "AirDriftTime": 0.1, "SlipStreamSpd": 4, "SlipTime": 0.3}},
        {"name": "Spooky Exhaust", "stats": {"CoinBoostTime": -0.5, "MaxCoinsSpd": 1.6, "AirDriftTime": 0.2, "SlipStreamRadius": 30, "SlipTime": 1, "T1": 0.4}},
        {"name": "Heavy Exhaust", "stats": {"CoinBoostTime": 1, "StartCoins": 1, "MaxCoins": 2, "MaxCoinsSpd": 1, "BoostPads": 20}},
        {"name": "Simple Coin Exhaust", "stats": {"CoinBoostSpd": 3, "CoinBoostTime": 0.5}},
        {"name": "Starter Exhaust", "stats": {"CoinBoostSpd": 5, "CoinBoostTime": 0.3, "Speed": 0.3, "T2": 1}},
        {"name": "Polished Exhaust", "stats": {"CoinBoostTime": 1.3, "AirDriftTime": 0.1, "Speed": 0.25, "SlipStreamRadius": 18, "SlipStreamSpd": 2, "SlipTime": 1.4, "BoostPads": 13, "TrickSpd": 3}},
        {"name": "Ulti-Matey Exhaust", "stats": {"UltCharge": 7.5, "UltStart": 20}},
        {"name": "Gold Exhaust", "stats": {"AirDriftTime": 0.25, "TrickSpd": 7.5}},
    ],
    "SUSPENSION": [
        {"name": "Acrobatic Suspension", "stats": {"BoostPads": 10, "CoinBoostSpd": 5, "DriftSteer": 2, "Steer": 2, "AirDriftTime": 0.25, "Speed": -0.6, "SlipStreamRadius": 5, "SlipStreamSpd": 3.5, "SlipTime": 0.5, "TrickSpd": 3.5}},
        {"name": "Advanced Suspension", "stats": {"T1": 0.8, "T3": 0.5, "DriftSteer": 1.5, "Steer": 1.5, "AirDriftTime": 0.3, "UltStart": 10}},
        {"name": "Ice Suspension", "stats": {"T2": 1, "StartBoost": -5, "DriftSteer": -1.5, "Steer": -1.5, "AirDriftTime": 0.2, "Speed": 1, "SlowAreaPenalty": 0.3, "TrickSpd": 3}},
        {"name": "First Charge Suspension", "stats": {"T1": 3.2, "T2": -2, "T3": -2, "DriftSteer": 0.5, "Steer": 0.5, "Daze": -6, "UltCharge": 3}},
        {"name": "Fresh Suspension", "stats": {}},
        {"name": "Spooky Suspension", "stats": {"BoostPads": 5, "T1": 1, "MaxCoinsSpd": 0.8, "DriftSteer": 2, "Steer": 2, "AirDriftTime": 0.1, "Speed": 0.2, "SlowAreaPenalty": 0.3, "Daze": -20}},
        {"name": "Slime Suspension", "stats": {"T1": 1.6, "T2": 0.5, "T3": -0.5, "StartBoost": 8, "StartCoins": 1, "SlipStreamRadius": 10, "SlipStreamSpd": 5.5}},
        {"name": "Locked Suspension", "stats": {"Speed": 1.2, "Daze": 60}},
        {"name": "No Drift Suspension", "stats": {"T1": -0.6, "T2": -0.8, "T3": -1.2, "CoinBoostSpd": 5, "DriftSteer": -5, "Steer": 30, "Speed": 2, "Daze": 10}},
        {"name": "Peanutician Suspension", "stats": {"T1": 0.8, "DriftSteer": 2.2, "Steer": 2.2, "AirDriftTime": 1, "SlowAreaPenalty": 0.6}},
        {"name": "Snail Suspension", "stats": {"BoostPads": 10, "DriftSteer": -1, "Steer": -1, "Daze": -10, "UltCharge": 3}},
        {"name": "Starter Suspension", "stats": {"DriftSteer": 1.2, "Steer": 1.2, "Daze": -15, "UltStart": 7}},
        {"name": "Train Suspension", "stats": {"BoostPads": 15, "T1": 0.3, "T2": 0.3, "T3": 0.3, "StartBoost": 15, "DriftSteer": -2, "Steer": -2, "AirDriftTime": 0.2, "Speed": 1.3, "Daze": 25, "UltCharge": 3}},
        {"name": "Polished Suspension", "stats": {"BoostPads": 5, "DriftSteer": 0.5, "Steer": 0.5, "Speed": 0.5, "Daze": -15}},
    ],
    "GEARBOX": [
        {"name": "Advanced Gearbox", "stats": {"T1": 1, "T2": 0.6, "T3": 1.5, "DriftSteer": 0.5}},
        {"name": "Chaotic Gearbox", "stats": {"T1": -1.6, "T2": 3.2, "T3": -2, "Daze": -10}},
        {"name": "Gamers Gearbox", "stats": {"T1": -1, "T2": 0.5, "T3": 1.85, "AirDriftTime": 0.4}},
        {"name": "Fresh Gearbox", "stats": {"T1": 0.3, "T2": 0.4, "T3": 0.6, "AirDriftTime": 0.1}},
        {"name": "The Front Runner", "stats": {"T1": 0.4, "T2": 0.7, "T3": 1.2, "StartBoost": 12}},
        {"name": "Grass Gearbox", "stats": {"T1": 0.4, "T2": 0.5, "T3": 1}},
        {"name": "Spooky Gearbox", "stats": {"T1": 0.4, "T2": 2, "T3": 0.6, "AirDriftTime": 0.1}},
        {"name": "Dragon Head Gearbox", "stats": {"T1": 1.8, "T3": 1, "StartBoost": 5, "CoinBoostTime": 1, "StartCoins": 1}},
        {"name": "Efficient Gearbox", "stats": {"BoostPads": 7.5, "T1": 2.1, "T2": 1, "T3": -1.2, "StartBoost": 10, "DriftSteer": -0.5, "Steer": -0.5, "Speed": 0.5, "SlipStreamRadius": 20, "SlipStreamSpd": 3.5, "TrickSpd": 2.5}},
        {"name": "Ice Gearbox", "stats": {"DriftSteer": 1, "Steer": 1, "Speed": 1}},
        {"name": "No Drift Gearbox", "stats": {"T1": -0.8, "T2": -1, "T3": -2, "Speed": 2.5, "Daze": -12, "UltStart": 20, "SlipStreamRadius": 10, "SlipStreamSpd": 3.5, "SlipTime": 1}},
        {"name": "Razor Gearbox", "stats": {"T1": 1.4, "T3": 0.4, "DriftSteer": -0.5, "Steer": -0.5}},
        {"name": "Recovery Gold Gearbox", "stats": {"T1": 1.8, "Daze": -30}},
        {"name": "Marine Gearbox", "stats": {"T1": 1.2, "Daze": -20}},
        {"name": "Starter Gearbox", "stats": {"DriftRate": -2.5, "T1": 0.4, "T2": 0.5, "T3": 1, "DriftSteer": 1, "Steer": 1}},
        {"name": "Hasty Gearbox", "stats": {"DriftRate": 2.5, "T1": -1.6, "T2": 2, "T3": 1.35}},
        {"name": "Ancient Gearbox", "stats": {"T1": 0.85, "T2": 1.3, "T3": 1.1}},
        {"name": "Polished Gearbox", "stats": {"DriftRate": 10, "T1": -0.8, "T2": -1, "T3": -1}},
    ],
    "TRINKET": [
        {"name": "Electronic Key", "stats": {"DriftSteer": 0.5, "Steer": 0.5, "UltCharge": 5, "SlipStreamRadius": 10, "SlipStreamSpd": 3}},
        {"name": "Gold Tags", "stats": {"BoostPads": 15, "T3": 1, "StartCoins": 1, "SlipStreamRadius": 20}},
        {"name": "Skull Collar", "stats": {"StartBoost": -15, "MaxCoins": 5, "MaxCoinsSpd": 0.8, "Daze": -10, "UltCharge": 5}},
        {"name": "Turtle Trinket", "stats": {"CoinBoostSpd": 10, "CoinBoostTime": 1, "DriftSteer": 2, "Steer": 2, "UltCharge": 3, "TrickSpd": 2}},
        {"name": "Tank Trinket", "stats": {"T2": 1, "T3": 1, "StartBoost": -5, "MaxCoinsSpd": 0.4, "DriftSteer": -2, "Speed": 0.4, "SlowAreaPenalty": -20, "Daze": 5}},
        {"name": "Capytulator", "stats": {"BoostPads": 17.5, "MaxCoinsSpd": 0.5, "Daze": 60, "UltCharge": 5}},
        {"name": "Air Freshener", "stats": {"T1": 1.6, "TrickSpd": 8}},
        {"name": "Fast Runner", "stats": {"T1": 1.6}},
        {"name": "Cauldron", "stats": {"T1": 0.5, "T2": 0.4, "T3": 0.3, "CoinBoostTime": 0.5, "Speed": 1}},
        {"name": "Fire Keys", "stats": {"T1": 0.8, "T2": 0.4, "T3": 0.4, "StartCoins": 1, "MaxCoins": 1, "MaxCoinsSpd": 0.5, "SlowAreaPenalty": -20, "UltStart": 10, "SlipStreamRadius": 15, "SlipStreamSpd": 5.5}},
        {"name": "Lucky Dice", "stats": {"T1": 1.6, "StartBoost": 8, "StartCoins": 2, "UltStart": 15, "SlipStreamRadius": 12, "SlipStreamSpd": 20, "SlipTime": 1}},
        {"name": "Inheritance", "stats": {"StartCoins": 5, "MaxCoinsSpd": -0.5}},
        {"name": "Voodoo", "stats": {"MaxCoins": -1}},
        {"name": "Community Card", "stats": {"BoostPads": 5, "T1": 0.6, "T2": 0.4, "T3": 0.5, "CoinBoostTime": 0.5, "MaxCoinsSpd": 0.25, "AirDriftTime": 0.07, "Speed": 0.25}},
        {"name": "Ducky", "stats": {"SlowAreaPenalty": -20, "SlipStreamRadius": 25, "SlipStreamSpd": 6.5, "SlipTime": 3}},
        {"name": "Anchor", "stats": {"BoostPads": 10, "SlowAreaPenalty": 50, "Daze": -20, "UltStart": 10}},
        {"name": "Disco Ball", "stats": {"BoostPads": 12, "CoinBoostSpd": 15, "CoinBoostTime": 0.5, "TrickSpd": 3}},
        {"name": "Starter Keys", "stats": {"BoostPads": 10, "T1": 0.8, "UltStart": 15}},
        {"name": "Toxic Tag", "stats": {"DriftRate": -8, "T3": 1.5, "MaxCoinsSpd": 0.2, "DriftSteer": -1, "Steer": -1, "Speed": 0.2, "SlowAreaPenalty": -30, "UltCharge": 4}},
        {"name": "Tourney Tag", "stats": {"StartBoost": 15, "CoinBoostTime": 1.8, "Speed": 0.2, "UltStart": 15, "TrickSpd": 2}},
        {"name": "Water Rider", "stats": {"BoostPads": 5, "DriftSteer": 1, "Steer": 1, "SlowAreaPenalty": 80, "Daze": -10, "UltCharge": -20, "SlipStreamSpd": 6.5, "SlipTime": 1.5, "TrickSpd": 2.5}},
    ],
}


# =========================================================
# 2) CHARACTERS (you can edit/extend later)
# =========================================================
CHARACTERS_RAW = [
    {"name": "Bulma", "Speed": 4.1, "Drift Power": 4.1, "Coin Boost": 4.1, "Handling": 4.1, "Style": 4.1},
    {"name": "Capy", "Speed": 4.1, "Drift Power": 4.1, "Coin Boost": 4.8, "Handling": 3.9, "Style": 4.5},
    {"name": "Chibben", "Speed": 4.3, "Drift Power": 4.1, "Coin Boost": 4.1, "Handling": 3.9, "Style": 5.1},
    {"name": "Chimpanzee", "Speed": 4.3, "Drift Power": 4.8, "Coin Boost": 4.2, "Handling": 4.3, "Style": 3.6},
    {"name": "CL", "Speed": 4.5, "Drift Power": 4.1, "Coin Boost": 3.6, "Handling": 4.2, "Style": 4.1},
    {"name": "Cobie", "Speed": 5.0, "Drift Power": 3.6, "Coin Boost": 4.2, "Handling": 3.3, "Style": 3.6},
    {"name": "Loma", "Speed": 4.4, "Drift Power": 4.1, "Coin Boost": 4.2, "Handling": 4.3, "Style": 4.4},
    {"name": "Ohbibi", "Speed": 4.5, "Drift Power": 3.6, "Coin Boost": 4.1, "Handling": 4.1, "Style": 4.4},
    {"name": "Ohbobot", "Speed": 5.0, "Drift Power": 4.2, "Coin Boost": 4.2, "Handling": 4.4, "Style": 4.2},
    {"name": "Suited Shiba", "Speed": 4.2, "Drift Power": 3.9, "Coin Boost": 4.4, "Handling": 4.2, "Style": 4.8},
    {"name": "Vanilla Gorilla", "Speed": 4.1, "Drift Power": 4.2, "Coin Boost": 3.6, "Handling": 4.8, "Style": 4.3},
    {"name": "Zach", "Speed": 4.4, "Drift Power": 4.1, "Coin Boost": 4.1, "Handling": 4.3, "Style": 4.4},
]

# Drift Power split across tiers (mostly T3)
DP_SPLIT = (0.15, 0.15, 0.70)  # T1, T2, T3
assert abs(sum(DP_SPLIT) - 1.0) < 1e-6


# =========================================================
# 3) CONSTANTS
# =========================================================
CATEGORIES = ["CHARACTER", "ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX", "TRINKET"]
MAIN_SCORES = ["race", "coin", "drift", "combat"]

RAW_STAT_KEYS = [
    "Speed", "StartBoost", "SlipStreamSpd", "SlowAreaPenalty",
    "StartCoins", "MaxCoins", "CoinBoostSpd", "CoinBoostTime",
    "DriftSteer", "Steer", "AirDriftTime",
    "UltCharge", "Daze", "SlipStreamRadius",
    "TrickSpd", "BoostPads", "MaxCoinsSpd", "SlipTime", "UltStart", "DriftRate",
    "T1", "T2", "T3",
]
RAW_STAT_KEYS = list(dict.fromkeys(RAW_STAT_KEYS))
KEY2IDX = {k: i for i, k in enumerate(RAW_STAT_KEYS)}

# Main score formulas
RACE_COEFFS = {"Speed": 2.0, "StartBoost": 1.5, "SlipStreamSpd": 1.2, "SlowAreaPenalty": -1.0}
COIN_COEFFS = {"StartCoins": 1.0, "MaxCoins": 2.0, "CoinBoostSpd": 1.5, "CoinBoostTime": 1.5}
DRIFT_COEFFS = {"DriftSteer": 2.0, "Steer": 1.5, "AirDriftTime": 1.0}
COMBAT_COEFFS = {"UltCharge": 2.0, "Daze": 1.5, "SlipStreamRadius": 1.0}

PRIORITY_MAP = {"Low": 0.0, "Medium": 2.5, "High": 5.0}

# Stats summary sections
PERCENT_STATS = {"BoostPads", "SlowAreaPenalty", "DriftRate", "UltCharge", "Daze"}
STAT_SECTIONS = [
    ("Movement & Speed", "↗", [
        ("Speed", "c-blue"),
        ("StartBoost", "c-orange"),
        ("BoostPads", "c-yellow"),
        ("SlowAreaPenalty", "c-red"),
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


# =========================================================
# 4) CSS
# =========================================================
LEGEND_CSS = r"""
<style>
.legend-wrap{
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 12px 14px;
    background: rgba(255,255,255,0.02);
}
.legend-h{
    font-weight: 1000;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin: 10px 0 6px 0;
    font-size: 12px;
    color: rgba(190,200,220,0.72);
}
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

[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(1200px 700px at 18% 10%, rgba(16,54,51,0.22), rgba(0,0,0,0)),
        radial-gradient(900px 600px at 90% 0%, rgba(10,18,18,0.55), rgba(0,0,0,0)),
        linear-gradient(180deg, #050707 0%, #070b0b 45%, #050707 100%);
}
[data-testid="stHeader"]{ background: rgba(0,0,0,0); }

[data-testid="stSidebar"]{
    background:
        radial-gradient(1000px 450px at 20% 0%, rgba(16,54,51,0.18), rgba(0,0,0,0)),
        linear-gradient(180deg, #060909 0%, #070d0d 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] div.block-container { padding-top: 1rem; }

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

div[data-testid="stSlider"]{
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
    padding: 0.1rem 0 0.2rem 0 !important;
}
div[data-testid="stSlider"] > div{
    background: transparent !important;
}

/* Build badge */
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
.badge-wrap{ display:flex; align-items:center; }
.badge-wrap p{ margin:0 !important; }
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


# =========================================================
# 5) CHAR DB BUILDER (ABSOLUTE baseline, Drift Power mostly T3)
# =========================================================
def build_character_database_from_raw(rows, dp_split=DP_SPLIT):
    """
    Characters are stored as ABSOLUTE baselines.
    Gear adds on top; optimiser scores GEAR GAIN (totals - character).
    """
    t1w, t2w, t3w = dp_split
    out = []
    for r in rows:
        name = str(r["name"]).strip()

        spd = float(r["Speed"])
        handling = float(r["Handling"])
        style = float(r["Style"])
        coin = float(r["Coin Boost"])
        dp = float(r["Drift Power"])

        stats = {
            "Speed": spd,
            "Steer": handling,
            "DriftSteer": handling,
            "TrickSpd": style,            # Style -> Trick jump stat
            "CoinBoostSpd": coin,         # Coin Boost -> coin boost speed
            "T1": dp * t1w,               # Drift Power -> tiers (mostly T3)
            "T2": dp * t2w,
            "T3": dp * t3w,
        }
        out.append({"name": name, "stats": stats})
    return out


CHARACTER_DATABASE = build_character_database_from_raw(CHARACTERS_RAW)


# =========================================================
# 6) DATA + SCORING
# =========================================================
@st.cache_data(show_spinner=False)
def df_from_category(category, stat_keys):
    if category == "CHARACTER":
        source = CHARACTER_DATABASE
    else:
        source = PARTS_DATABASE.get(category, [])

    rows = []
    for item in source:
        row = {"name": item.get("name", "")}
        stats = item.get("stats", {}) or {}
        for k in stat_keys:
            row[k] = float(stats.get(k, 0.0))
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=["name"] + list(stat_keys))
    return df


def compute_main_scores(totals: np.ndarray):
    Speed = totals[:, KEY2IDX["Speed"]]
    StartBoost = totals[:, KEY2IDX["StartBoost"]]
    SlipStreamSpd = totals[:, KEY2IDX["SlipStreamSpd"]]
    SlowAreaPenalty = totals[:, KEY2IDX["SlowAreaPenalty"]]

    StartCoins = totals[:, KEY2IDX["StartCoins"]]
    MaxCoins = totals[:, KEY2IDX["MaxCoins"]]
    CoinBoostSpd = totals[:, KEY2IDX["CoinBoostSpd"]]
    CoinBoostTime = totals[:, KEY2IDX["CoinBoostTime"]]

    DriftSteer = totals[:, KEY2IDX["DriftSteer"]]
    Steer = totals[:, KEY2IDX["Steer"]]
    AirDriftTime = totals[:, KEY2IDX["AirDriftTime"]]

    UltCharge = totals[:, KEY2IDX["UltCharge"]]
    Daze = totals[:, KEY2IDX["Daze"]]
    SlipStreamRadius = totals[:, KEY2IDX["SlipStreamRadius"]]

    race = (Speed * 2.0) + (StartBoost * 1.5) + (SlipStreamSpd * 1.2) - SlowAreaPenalty
    coin = (StartCoins * 1.0) + (MaxCoins * 2.0) + (CoinBoostSpd * 1.5) + (CoinBoostTime * 1.5)
    drift = (DriftSteer * 2.0) + (Steer * 1.5) + AirDriftTime
    combat = (UltCharge * 2.0) + (Daze * 1.5) + SlipStreamRadius
    return {"race": race, "coin": coin, "drift": drift, "combat": combat}


def _linear_score_df(df, coeffs):
    if df.empty:
        return np.array([], dtype=np.float32)
    s = np.zeros(len(df), dtype=np.float32)
    for k, c in coeffs.items():
        if k in df.columns:
            s += float(c) * df[k].to_numpy(np.float32)
    return s


@st.cache_data(show_spinner=False)
def compute_global_score_maxima():
    """
    Theoretical maxima for SCORES (0-100) are based on BEST POSSIBLE GEAR GAIN
    (characters are baseline, not part of the "max" target).

      best ENGINE + best EXHAUST + best SUSPENSION + best GEARBOX + best_two_trinkets
    """
    stat_keys = tuple(RAW_STAT_KEYS)
    dfE = df_from_category("ENGINE", stat_keys)
    dfX = df_from_category("EXHAUST", stat_keys)
    dfS = df_from_category("SUSPENSION", stat_keys)
    dfG = df_from_category("GEARBOX", stat_keys)
    dfT = df_from_category("TRINKET", stat_keys)

    def best_single(df, coeffs):
        s = _linear_score_df(df, coeffs)
        return float(s.max()) if s.size else 0.0

    def best_two_trinkets(dfT_, coeffs):
        s = _linear_score_df(dfT_, coeffs)
        if s.size < 2:
            return 0.0
        top2 = np.partition(s, -2)[-2:]
        return float(top2.sum())

    maxima = {
        "race": best_single(dfE, RACE_COEFFS) + best_single(dfX, RACE_COEFFS) + best_single(dfS, RACE_COEFFS) + best_single(dfG, RACE_COEFFS) + best_two_trinkets(dfT, RACE_COEFFS),
        "coin": best_single(dfE, COIN_COEFFS) + best_single(dfX, COIN_COEFFS) + best_single(dfS, COIN_COEFFS) + best_single(dfG, COIN_COEFFS) + best_two_trinkets(dfT, COIN_COEFFS),
        "drift": best_single(dfE, DRIFT_COEFFS) + best_single(dfX, DRIFT_COEFFS) + best_single(dfS, DRIFT_COEFFS) + best_single(dfG, DRIFT_COEFFS) + best_two_trinkets(dfT, DRIFT_COEFFS),
        "combat": best_single(dfE, COMBAT_COEFFS) + best_single(dfX, COMBAT_COEFFS) + best_single(dfS, COMBAT_COEFFS) + best_single(dfG, COMBAT_COEFFS) + best_two_trinkets(dfT, COMBAT_COEFFS),
    }
    return maxima


def normalize_scores_global(df):
    df = df.copy()
    max_scores = compute_global_score_maxima()
    for k in MAIN_SCORES:
        vmax = float(max_scores.get(k, 0.0))
        df[f"{k}_raw"] = df[k].astype(float)
        df[f"{k}_max"] = vmax
        df[f"{k}_norm"] = (df[k].astype(float) / vmax) * 100.0 if vmax > 0 else 0.0
    return df


def score_from_gear_delta(totals_abs: np.ndarray, char_vec_abs: np.ndarray):
    """
    totals_abs includes character + gear.
    We score using gear_gain = totals_abs - character (baseline).
    """
    delta = totals_abs - char_vec_abs
    return compute_main_scores(delta)


# =========================================================
# 7) OPTIMISER
# =========================================================
@dataclass
class OptimiseConfig:
    top_n: int = 20
    weights_main: dict = field(default_factory=dict)
    weights_raw: dict = field(default_factory=dict)
    constraints_main: dict = field(default_factory=dict)


def optimise_builds(inventory, config: OptimiseConfig):
    if not config.weights_main:
        config.weights_main = {"race": 1.0, "coin": 0.0, "drift": 0.0, "combat": 0.0}
    if config.weights_raw is None:
        config.weights_raw = {}
    if config.constraints_main is None:
        config.constraints_main = {}

    stat_keys = tuple(RAW_STAT_KEYS)
    dfC = df_from_category("CHARACTER", stat_keys)
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

    # character is selected as a single choice (we keep it as a 1-row df)
    dfC = _filter(dfC, inventory["CHARACTER"], "CHARACTER")
    dfE = _filter(dfE, inventory["ENGINE"], "ENGINE")
    dfX = _filter(dfX, inventory["EXHAUST"], "EXHAUST")
    dfS = _filter(dfS, inventory["SUSPENSION"], "SUSPENSION")
    dfG = _filter(dfG, inventory["GEARBOX"], "GEARBOX")
    dfT = _filter(dfT, inventory["TRINKET"], "TRINKET")

    if len(dfT) < 2:
        raise ValueError("Select at least 2 trinkets (duplicates are not allowed).")

    C_arr = dfC[RAW_STAT_KEYS].to_numpy(np.float32)   # (1, K)
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

    # gear-only base
    base_gear = E_arr[idx_e] + X_arr[idx_x] + S_arr[idx_s] + G_arr[idx_g]
    nbase = base_gear.shape[0]

    # character baseline vector
    char_vec = C_arr[0]  # absolute baseline

    # unique trinket pairs (no duplicates)
    t1, t2 = np.triu_indices(T, k=1)
    pair_stats = T_arr[t1] + T_arr[t2]

    results = []
    top_n = int(config.top_n)

    for p_i in range(pair_stats.shape[0]):
        totals_abs = base_gear + char_vec + pair_stats[p_i]
        scores = score_from_gear_delta(totals_abs, char_vec)  # SCORED ON GEAR GAIN

        # constraints apply to GEAR GAIN scores (same as optimiser objective)
        mask = np.ones(nbase, dtype=bool)
        for k, (lo, hi) in config.constraints_main.items():
            if lo is not None:
                mask &= scores[k] >= float(lo)
            if hi is not None:
                mask &= scores[k] <= float(hi)
        if not mask.any():
            continue

        obj = np.zeros(nbase, dtype=np.float32)
        for k, w in config.weights_main.items():
            obj += float(w) * scores[k].astype(np.float32)

        # raw stat priorities also apply to GEAR GAIN, not character baseline
        for raw, w in config.weights_raw.items():
            if raw in KEY2IDX:
                gain = (totals_abs[:, KEY2IDX[raw]] - char_vec[KEY2IDX[raw]]).astype(np.float32)
                obj += float(w) * gain

        obj[~mask] = -np.inf
        kkeep = min(top_n, int(mask.sum()))
        cand = np.argpartition(obj, -kkeep)[-kkeep:]
        cand = cand[np.argsort(obj[cand])[::-1]]

        for i in cand[:kkeep]:
            results.append((
                float(obj[i]),
                float(scores["race"][i]),
                float(scores["coin"][i]),
                float(scores["drift"][i]),
                float(scores["combat"][i]),
                dfC.loc[0, "name"],
                dfE.loc[idx_e[i], "name"],
                dfX.loc[idx_x[i], "name"],
                dfS.loc[idx_s[i], "name"],
                dfG.loc[idx_g[i], "name"],
                dfT.loc[t1[p_i], "name"],
                dfT.loc[t2[p_i], "name"],
            ))

    cols = [
        "objective", "race", "coin", "drift", "combat",
        "CHARACTER", "ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX",
        "TRINKET_1", "TRINKET_2",
    ]
    if not results:
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(results, columns=cols)
    df = df.sort_values("objective", ascending=False).drop_duplicates(
        subset=["CHARACTER", "ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX", "TRINKET_1", "TRINKET_2"]
    ).head(top_n).reset_index(drop=True)
    return df


# =========================================================
# 8) RANGES FOR SLIDERS (advanced constraints)
# =========================================================
def _minmax(df, keys):
    mn, mx = {}, {}
    for k in keys:
        mn[k] = float(df[k].min()) if (not df.empty and k in df.columns) else 0.0
        mx[k] = float(df[k].max()) if (not df.empty and k in df.columns) else 0.0
    return mn, mx


def _trinket_pair_minmax(dfT, keys):
    arr = dfT[keys].to_numpy(np.float32)
    T = len(dfT)
    t1, t2 = np.triu_indices(T, k=1)
    pairs = arr[t1] + arr[t2]
    mn = {k: float(pairs[:, i].min()) for i, k in enumerate(keys)}
    mx = {k: float(pairs[:, i].max()) for i, k in enumerate(keys)}
    return mn, mx


def _lin_minmax(total_min, total_max, coeffs):
    lo, hi = 0.0, 0.0
    for k, c in coeffs.items():
        if c >= 0:
            lo += c * total_min.get(k, 0.0)
            hi += c * total_max.get(k, 0.0)
        else:
            lo += c * total_max.get(k, 0.0)
            hi += c * total_min.get(k, 0.0)
    return float(lo), float(hi)


def estimate_main_score_ranges(dfC, dfE, dfX, dfS, dfG, dfT):
    """
    Constraints are for GEAR GAIN, so ranges ignore character baseline.
    (dfC included in signature/UI, but not used here.)
    """
    needed = list(set(list(RACE_COEFFS) + list(COIN_COEFFS) + list(DRIFT_COEFFS) + list(COMBAT_COEFFS)))
    e_mn, e_mx = _minmax(dfE, needed)
    x_mn, x_mx = _minmax(dfX, needed)
    s_mn, s_mx = _minmax(dfS, needed)
    g_mn, g_mx = _minmax(dfG, needed)
    t_mn, t_mx = _trinket_pair_minmax(dfT, needed)

    total_min = {k: e_mn[k] + x_mn[k] + s_mn[k] + g_mn[k] + t_mn[k] for k in needed}
    total_max = {k: e_mx[k] + x_mx[k] + s_mx[k] + g_mx[k] + t_mx[k] for k in needed}

    rng = {
        "race": _lin_minmax(total_min, total_max, RACE_COEFFS),
        "coin": _lin_minmax(total_min, total_max, COIN_COEFFS),
        "drift": _lin_minmax(total_min, total_max, DRIFT_COEFFS),
        "combat": _lin_minmax(total_min, total_max, COMBAT_COEFFS),
    }
    out = {}
    for k, (lo, hi) in rng.items():
        pad = max(1.0, 0.05 * (hi - lo) if hi > lo else 1.0)
        out[k] = (lo - pad, hi + pad)
    return out


# =========================================================
# 9) STATS SUMMARY
# =========================================================
def _part_vec(cat, name):
    stat_keys = tuple(RAW_STAT_KEYS)
    df = df_from_category(cat, stat_keys)
    r = df[df["name"] == name]
    if r.empty:
        return np.zeros(len(RAW_STAT_KEYS), dtype=np.float32)
    return r[RAW_STAT_KEYS].to_numpy(np.float32)[0]


def totals_for_build_row_abs(row):
    v = (
        _part_vec("CHARACTER", row["CHARACTER"])
        + _part_vec("ENGINE", row["ENGINE"])
        + _part_vec("EXHAUST", row["EXHAUST"])
        + _part_vec("SUSPENSION", row["SUSPENSION"])
        + _part_vec("GEARBOX", row["GEARBOX"])
        + _part_vec("TRINKET", row["TRINKET_1"])
        + _part_vec("TRINKET", row["TRINKET_2"])
    )
    return {k: float(v[KEY2IDX[k]]) for k in RAW_STAT_KEYS}


def totals_for_build_row_gain(row):
    char_v = _part_vec("CHARACTER", row["CHARACTER"])
    abs_v = (
        char_v
        + _part_vec("ENGINE", row["ENGINE"])
        + _part_vec("EXHAUST", row["EXHAUST"])
        + _part_vec("SUSPENSION", row["SUSPENSION"])
        + _part_vec("GEARBOX", row["GEARBOX"])
        + _part_vec("TRINKET", row["TRINKET_1"])
        + _part_vec("TRINKET", row["TRINKET_2"])
    )
    gain_v = abs_v - char_v
    return {k: float(gain_v[KEY2IDX[k]]) for k in RAW_STAT_KEYS}


def render_stats_summary(stats, badge_text="01", title="Stat Summary"):
    def fmt(k, v):
        return f"{v:.2f}%" if k in PERCENT_STATS else f"{v:.2f}"

    parts = []
    parts.append('<div class="stats-card">')
    parts.append(
        f"""
        <div class="stats-title">
            <h3>{title}</h3>
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
    components_html_autosize(html, min_height=790, max_height=900, key=f"stats-{badge_text}-{title}".replace(" ", "_"))


# =========================================================
# 10) INVENTORY STATE + IMPORT BY TEXT
# =========================================================
GEAR_CATEGORIES = ["ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX", "TRINKET"]  # owned categories only


def init_owned_state(names_by_cat):
    if "owned" not in st.session_state:
        st.session_state["owned"] = {cat: {nm: False for nm in names_by_cat[cat]} for cat in GEAR_CATEGORIES}
    else:
        owned = st.session_state["owned"]
        for cat in GEAR_CATEGORIES:
            owned.setdefault(cat, {})
            for nm in names_by_cat[cat]:
                owned[cat].setdefault(nm, False)

    st.session_state.setdefault("chip_version", 0)
    st.session_state.setdefault("selected_build_idx", -1)
    st.session_state.setdefault("show_stats", False)
    st.session_state.setdefault("results_df", None)
    st.session_state.setdefault("last_run_sig", None)
    st.session_state.setdefault("import_text", "")


def set_all_owned(value, names_by_cat):
    owned = st.session_state["owned"]
    for cat, names in names_by_cat.items():
        if cat not in owned:
            continue
        for nm in names:
            owned[cat][nm] = bool(value)
    st.session_state["chip_version"] += 1


def on_chip_change(cat, nm, widget_key):
    st.session_state["owned"][cat][nm] = bool(st.session_state[widget_key])


def part_toggle_grid(cat, names):
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
    for cat in GEAR_CATEGORIES:
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
        if cat not in GEAR_CATEGORIES:
            continue
        owned[cat][nm] = True
        applied += 1

    st.session_state["chip_version"] += 1
    return applied, unknown, amb


# =========================================================
# 11) RESULTS TABLE RENDER + inline details drawer
# =========================================================
def components_html_autosize(html: str, *, min_height: int = 50, max_height: int = 2000, key: str | None = None):
    if key is None:
        key = str(uuid.uuid4())
    wrapper_id = f"autosize-{key}"

    rendered = f"""
    <div id="{wrapper_id}">{html}</div>
    <script>
    (function() {{
        const MIN_H = {int(min_height)};
        const MAX_H = {int(max_height)};
        function clamp(x) {{ return Math.max(MIN_H, Math.min(MAX_H, x)); }}

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
                {{ isStreamlitMessage: true, type: "streamlit:setFrameHeight", height }},
                "*"
            );
        }}

        window.addEventListener("load", postHeight);
        window.addEventListener("resize", () => requestAnimationFrame(postHeight));

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


def render_build_table(df):
    selected = int(st.session_state.get("selected_build_idx", -1))
    show_stats = bool(st.session_state.get("show_stats", False))
    max_scores = compute_global_score_maxima()

    ROW_CARD_CSS = r"""
    <style>
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
        position: relative;
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
        z-index: 9999;
    }
    .score-race .score-name{ color: rgba(120,170,255,0.98); }
    .score-coin .score-name{ color: rgba(255,215,90,0.98); }
    .score-drift .score-name{ color: rgba(190,140,255,0.98); }
    .score-combat .score-name{ color: rgba(255,120,120,0.98); }
    </style>
    """

    for i, r in df.iterrows():
        badge = str(i + 1).zfill(2)

        h1, h2 = st.columns([0.7, 0.20], vertical_alignment="center")
        with h1:
            st.markdown(
                f'<div class="badge-wrap"><div class="build-badge">{badge}</div></div>',
                unsafe_allow_html=True
            )

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

            tip = f"{pct:.1f}% of Max Gear Gain | Raw:{raw:.1f} | Max={vmax:.1f}"
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
                    <div class="part-chip"><div class="part-label">CHARACTER</div><div class="part-name">{r["CHARACTER"]}</div></div>
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

        components_html_autosize(ROW_CARD_CSS + row_html, min_height=220, max_height=520, key=f"row-{i}")

        if show_stats and selected == i:
            gain_stats = totals_for_build_row_gain(r)
            abs_stats = totals_for_build_row_abs(r)
            render_stats_summary(gain_stats, badge_text=badge, title="Gear Gain (adds onto character)")
            render_stats_summary(abs_stats, badge_text=badge, title="Absolute (character + gear)")


# =========================================================
# 12) RUN SIGNATURE + RESULTS CACHING
# =========================================================
def make_run_signature(inventory, cfg):
    inv_sig = tuple((cat, tuple(sorted(inventory.get(cat, [])))) for cat in CATEGORIES)
    w_main_sig = tuple(sorted(cfg.weights_main.items()))
    w_raw_sig = tuple(sorted(cfg.weights_raw.items()))
    c_sig = tuple(sorted((k, cfg.constraints_main.get(k, (None, None))) for k in MAIN_SCORES))
    return (inv_sig, w_main_sig, w_raw_sig, c_sig, int(cfg.top_n))


# =========================================================
# 13) APP
# =========================================================
st.set_page_config(page_title="OBK Gear Optimiser", layout="wide")
st.markdown(APP_CSS, unsafe_allow_html=True)
st.markdown(LEGEND_CSS, unsafe_allow_html=True)

st.title("OBK Gear Optimiser")
st.caption("By Ellyess")

missing = [c for c in ["ENGINE", "EXHAUST", "SUSPENSION", "GEARBOX", "TRINKET"] if c not in PARTS_DATABASE]
if missing:
    st.error(f"PARTS_DATABASE missing categories: {missing}. Paste your full database at the top of this file.")
    st.stop()

stat_keys = tuple(RAW_STAT_KEYS)

# Character selection (single)
char_names = sorted(df_from_category("CHARACTER", stat_keys)["name"].astype(str).tolist(), key=lambda x: x.lower())
if not char_names:
    st.error("No characters found. Fill CHARACTER_DATABASE / CHARACTERS_RAW.")
    st.stop()

st.sidebar.header("Character")
selected_character = st.sidebar.selectbox("Pick your character", char_names, index=0)
st.sidebar.caption(f"Character baseline is ABSOLUTE | Drift Power split: {DP_SPLIT}")
st.sidebar.markdown("---")

# Build gear lists
names_by_cat = {
    cat: sorted(df_from_category(cat, stat_keys)["name"].astype(str).tolist(), key=lambda x: x.lower())
    for cat in GEAR_CATEGORIES
}
init_owned_state(names_by_cat)

# Sidebar: import first (gear only)
st.sidebar.header("0) Import owned equipment (gear only)")
st.sidebar.caption("Paste gear names separated by newlines or commas. Unknown names will be reported.")
st.sidebar.text_area("Owned equipment list", key="import_text", height=120, placeholder="e.g.\nFresh Engine\nCyber Exhaust\nLucky Dice")

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

# Sidebar: inventory selection (gear)
st.sidebar.header("1) Click to select what you have")
inventory = {cat: part_toggle_grid(cat, names_by_cat[cat]) for cat in GEAR_CATEGORIES}
inventory["CHARACTER"] = [selected_character]

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

# Main priorities
st.sidebar.markdown("---")
st.sidebar.header("2) Priority (simple)")
p_race = st.sidebar.selectbox("Race priority", ["Low", "Medium", "High"], index=1)
p_coin = st.sidebar.selectbox("Coin priority", ["Low", "Medium", "High"], index=0)
p_drift = st.sidebar.selectbox("Drift priority", ["Low", "Medium", "High"], index=0)
p_combat = st.sidebar.selectbox("Combat priority", ["Low", "Medium", "High"], index=0)

w_race = PRIORITY_MAP[p_race]
w_coin = PRIORITY_MAP[p_coin]
w_drift = PRIORITY_MAP[p_drift]
w_combat = PRIORITY_MAP[p_combat]

# Raw priorities (optional)
st.sidebar.markdown("**Raw stat priorities (optional)**")
raw_choices = [
    "TrickSpd", "AirDriftTime", "DriftSteer", "Steer",
    "Speed", "StartBoost", "SlipStreamSpd",
    "StartCoins", "MaxCoins", "CoinBoostSpd", "CoinBoostTime",
    "UltCharge", "Daze", "SlipStreamRadius",
    "MaxCoinsSpd", "SlipTime", "UltStart", "DriftRate",
    "T1", "T2", "T3",
]
raw_choices = [x for x in raw_choices if x in KEY2IDX]

selected_raw = st.sidebar.multiselect("Include these raw stats in objective (GEAR GAIN)", raw_choices, default=[])
weights_raw = {}
for raw in selected_raw:
    level = st.sidebar.selectbox(
        f"{raw} priority",
        ["Low", "Medium", "High"],
        index=1,
        key=f"rawprio::{raw}",
    )
    weights_raw[raw] = PRIORITY_MAP[level]

top_n = st.sidebar.slider("How many results?", 1, 8, 3, 1)

# Constraints (simple + advanced)
st.sidebar.markdown("---")
st.sidebar.header("3) Conditions")
enable_constraints = st.sidebar.checkbox("Enable constraints", value=True)

constraints_main = {}
if enable_constraints:
    simple_above_zero = st.sidebar.checkbox("Simple: keep scores above zero (GEAR GAIN)", value=False)
    if simple_above_zero:
        constraints_main.update({
            "race": (0.0, None),
            "coin": (0.0, None),
            "drift": (0.0, None),
            "combat": (0.0, None),
        })

    with st.sidebar.expander("Advanced constraints (min/max sliders) (GEAR GAIN)", expanded=False):
        dfC_all = df_from_category("CHARACTER", stat_keys)
        dfE_all = df_from_category("ENGINE", stat_keys)
        dfX_all = df_from_category("EXHAUST", stat_keys)
        dfS_all = df_from_category("SUSPENSION", stat_keys)
        dfG_all = df_from_category("GEARBOX", stat_keys)
        dfT_all = df_from_category("TRINKET", stat_keys)

        dfC_sel = dfC_all[dfC_all["name"].isin(set(inventory["CHARACTER"]))].reset_index(drop=True)
        dfE_sel = dfE_all[dfE_all["name"].isin(set(inventory["ENGINE"]))].reset_index(drop=True)
        dfX_sel = dfX_all[dfX_all["name"].isin(set(inventory["EXHAUST"]))].reset_index(drop=True)
        dfS_sel = dfS_all[dfS_all["name"].isin(set(inventory["SUSPENSION"]))].reset_index(drop=True)
        dfG_sel = dfG_all[dfG_all["name"].isin(set(inventory["GEARBOX"]))].reset_index(drop=True)
        dfT_sel = dfT_all[dfT_all["name"].isin(set(inventory["TRINKET"]))].reset_index(drop=True)

        if len(dfT_sel) < 2:
            st.warning("Need at least 2 trinkets selected to use advanced constraints.")
        else:
            ranges = estimate_main_score_ranges(dfC_sel, dfE_sel, dfX_sel, dfS_sel, dfG_sel, dfT_sel)
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

run = st.sidebar.button("Run optimiser", type="primary")

# Build config
cfg = OptimiseConfig(
    top_n=int(top_n),
    weights_main={"race": w_race, "coin": w_coin, "drift": w_drift, "combat": w_combat},
    weights_raw=weights_raw,
    constraints_main=constraints_main,
)

# Show stale warning but keep results visible
current_sig = make_run_signature(inventory, cfg)
last_sig = st.session_state.get("last_run_sig")
if last_sig is not None and current_sig != last_sig:
    st.warning("You changed parts/priorities/conditions since the last run. Click **Run optimiser** to refresh results.")

# Run optimiser and STORE results
if run:
    for cat in GEAR_CATEGORIES:
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
    st.markdown(
        """
        <div class="legend-wrap">
            <div class="legend-h">Movement & Speed</div>
            <div class="legend-row"><div class="legend-key c-blue">Speed</div><div class="legend-val">Base speed increase.</div></div>
            <div class="legend-row"><div class="legend-key c-yellow">Boost Pads</div><div class="legend-val">Modifies the amount of speed boost pads give you.</div></div>
            <div class="legend-row"><div class="legend-key c-orange">Start Boost</div><div class="legend-val">Change in speed when successfully getting a start boost.</div></div>
            <div class="legend-row"><div class="legend-key c-cyan">SlipStream Spd</div><div class="legend-val">Extra speed while slipstreaming.</div></div>
            <div class="legend-row"><div class="legend-key c-purple">SlipStream Radius</div><div class="legend-val">Change in radius to detect a target to slipstream.</div></div>
            <div class="legend-row"><div class="legend-key c-cyan">SlipStream Time</div><div class="legend-val">Change in duration of slipstream boosts.</div></div>
            <div class="legend-row"><div class="legend-key c-red">SlowArea Penalty</div><div class="legend-val">Changes your speed on slow areas such as puddles. Higher is faster (less penalty).</div></div>
            <div class="legend-row"><div class="legend-key c-blue">Trick Spd</div><div class="legend-val">Modifies the amount of speed while under the effect of a trickjump boost.</div></div>

            <div class="legend-h">Handling & Drift</div>
            <div class="legend-row"><div class="legend-key c-purple">Drift Rate</div><div class="legend-val">The rate at which your drift bar fills when drifting. Higher is faster.</div></div>
            <div class="legend-row"><div class="legend-key c-purple">Drift Steer</div><div class="legend-val">Change in handling force while drifting.</div></div>
            <div class="legend-row"><div class="legend-key c-green">Steer</div><div class="legend-val">Change in handling force while NOT drifting.</div></div>
            <div class="legend-row"><div class="legend-key c-blue">AirDrift Time</div><div class="legend-val">Modifies the duration that you can maintain a drift while in the air (seconds).</div></div>

            <div class="legend-h">Coins & Economy</div>
            <div class="legend-row"><div class="legend-key c-yellow">Start Coins</div><div class="legend-val">Change in amount of coins you start the race with.</div></div>
            <div class="legend-row"><div class="legend-key c-orange">MaxCoins</div><div class="legend-val">Amount of coins needed to get coin boost and max coin speed.</div></div>
            <div class="legend-row"><div class="legend-key c-orange">MaxCoins Spd</div><div class="legend-val">Change in amount of speed on max coins (not CoinBoost Spd).</div></div>
            <div class="legend-row"><div class="legend-key c-yellow">CoinBoost Spd</div><div class="legend-val">Modifies the temporary speed boost on hitting max coins.</div></div>
            <div class="legend-row"><div class="legend-key c-yellow">CoinBoost Time</div><div class="legend-val">Modifies the duration of the speed boost on hitting max coins.</div></div>

            <div class="legend-h">Combat & Abilities</div>
            <div class="legend-row"><div class="legend-key c-pink">UltCharge</div><div class="legend-val">Changes the rate at which your ultimate bar fills.</div></div>
            <div class="legend-row"><div class="legend-key c-pink">UltStart</div><div class="legend-val">Changes the amount of ultimate charge you start a race with (flat amount).</div></div>
            <div class="legend-row"><div class="legend-key c-orange">Daze</div><div class="legend-val">Percentage change in duration of dazes inflicted on you. Higher is longer.</div></div>

            <div class="legend-h">Drift Tier Bonuses</div>
            <div class="legend-row"><div class="legend-key c-gray">T1</div><div class="legend-val">Amount of speed added on a tier 1 drift ignition.</div></div>
            <div class="legend-row"><div class="legend-key c-gray">T2</div><div class="legend-val">Amount of speed added on a tier 2 drift ignition.</div></div>
            <div class="legend-row"><div class="legend-key c-gray">T3</div><div class="legend-val">Amount of speed added on a tier 3 drift ignition.</div></div>

            <div class="legend-h">How scoring works</div>
            <div class="legend-row"><div class="legend-key c-gray">Scores (0–100)</div>
            <div class="legend-val">
                Scores are based on <b>GEAR GAIN</b> only (equipment added on top of your character).<br/>
                100% means “best possible gear gain” using the full equipment database.
            </div></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Render cached results
show = st.session_state.get("results_df")
if show is None or getattr(show, "empty", True):
    st.info("Select gear + choose a character + set priorities/conditions, then click **Run optimiser**.")
else:
    st.subheader("Builds")
    st.caption("Scores are 0–100 based on BEST POSSIBLE GEAR GAIN (not character). Hover a score for raw/max details.")
    render_build_table(show)

    st.download_button(
        "Download CSV",
        data=show.to_csv(index=False).encode("utf-8"),
        file_name="best_builds.csv",
        mime="text/csv",
        use_container_width=True,
    )
