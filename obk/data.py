"""
Data for OBK Gear Optimiser.
Includes parts database and data frame construction functions.
"""

import pandas as pd
import streamlit as st

from .constants import RAW_STAT_KEYS

###############################################################
# PARTS_DATABASE
###############################################################

# sourced from https://ohbabykart.wiki.gg/wiki/Equipment_Stats
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
        {"name": "Snail Engine", "stats": {"BoostPads": 10, "Speed": -2.5, "SlowDownSpd": 50, "Daze": -30, "UltCharge": 8, "UltStart": 18, "SlipStreamRadius": 30, "SlipStreamSpd": 7, "SlipTime": 0.8}},
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
        {"name": "Ice Suspension", "stats": {"T2": 1, "StartBoost": -5, "DriftSteer": -1.5, "Steer": -1.5, "AirDriftTime": 0.2, "Speed": 1, "SlowDownSpd": 30, "TrickSpd": 3}},
        {"name": "First Charge Suspension", "stats": {"T1": 3.2, "T2": -2, "T3": -2, "DriftSteer": 0.5, "Steer": 0.5, "Daze": -6, "UltCharge": 3}},
        {"name": "Fresh Suspension", "stats": {}},
        {"name": "Spooky Suspension", "stats": {"BoostPads": 5, "T1": 1, "MaxCoinsSpd": 0.8, "DriftSteer": 2, "Steer": 2, "AirDriftTime": 0.1, "Speed": 0.2, "SlowDownSpd": 30, "Daze": -20}},
        {"name": "Slime Suspension", "stats": {"T1": 1.6, "T2": 0.5, "T3": -0.5, "StartBoost": 8, "StartCoins": 1, "SlipStreamRadius": 10, "SlipStreamSpd": 5.5}},
        {"name": "Locked Suspension", "stats": {"Speed": 1.2, "Daze": 60}},
        {"name": "No Drift Suspension", "stats": {"T1": -0.6, "T2": -0.8, "T3": -1.2, "CoinBoostSpd": 5, "DriftSteer": -5, "Steer": 30, "Speed": 2, "Daze": 10}},
        {"name": "Peanutician Suspension", "stats": {"T1": 0.8, "DriftSteer": 2.2, "Steer": 2.2, "AirDriftTime": 1, "SlowDownSpd": 60}},
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
        {"name": "Tank Trinket", "stats": {"T2": 1, "T3": 1, "StartBoost": -5, "MaxCoinsSpd": 0.4, "DriftSteer": -2, "Speed": 0.4, "SlowDownSpd": -20, "Daze": 5}},
        {"name": "Capytulator", "stats": {"BoostPads": 17.5, "MaxCoinsSpd": 0.5, "Daze": 60, "UltCharge": 5}},
        {"name": "Air Freshener", "stats": {"T1": 1.6, "TrickSpd": 8}},
        {"name": "Fast Runner", "stats": {"T1": 1.6}},
        {"name": "Cauldron", "stats": {"T1": 0.5, "T2": 0.4, "T3": 0.3, "CoinBoostTime": 0.5, "Speed": 1}},
        {"name": "Fire Keys", "stats": {"T1": 0.8, "T2": 0.4, "T3": 0.4, "StartCoins": 1, "MaxCoins": 1, "MaxCoinsSpd": 0.5, "SlowDownSpd": -20, "UltStart": 10, "SlipStreamRadius": 15, "SlipStreamSpd": 5.5}},
        {"name": "Lucky Dice", "stats": {"T1": 1.6, "StartBoost": 8, "StartCoins": 2, "UltStart": 15, "SlipStreamRadius": 12, "SlipStreamSpd": 20, "SlipTime": 1}},
        {"name": "Inheritance", "stats": {"StartCoins": 5, "MaxCoinsSpd": -0.5}},
        {"name": "Voodoo", "stats": {"MaxCoins": -1}},
        {"name": "Community Card", "stats": {"BoostPads": 5, "T1": 0.6, "T2": 0.4, "T3": 0.5, "CoinBoostTime": 0.5, "MaxCoinsSpd": 0.25, "AirDriftTime": 0.07, "Speed": 0.25}},
        {"name": "Ducky", "stats": {"SlowDownSpd": -20, "SlipStreamRadius": 25, "SlipStreamSpd": 6.5, "SlipTime": 3}},
        {"name": "Anchor", "stats": {"BoostPads": 10, "SlowDownSpd": 50, "Daze": -20, "UltStart": 10}},
        {"name": "Disco Ball", "stats": {"BoostPads": 12, "CoinBoostSpd": 15, "CoinBoostTime": 0.5, "TrickSpd": 3}},
        {"name": "Starter Keys", "stats": {"BoostPads": 10, "T1": 0.8, "UltStart": 15}},
        {"name": "Toxic Tag", "stats": {"DriftRate": -8, "T3": 1.5, "MaxCoinsSpd": 0.2, "DriftSteer": -1, "Steer": -1, "Speed": 0.2, "SlowDownSpd": -30, "UltCharge": 4}},
        {"name": "Tourney Tag", "stats": {"StartBoost": 15, "CoinBoostTime": 1.8, "Speed": 0.2, "UltStart": 15, "TrickSpd": 2}},
        {"name": "Water Rider", "stats": {"BoostPads": 5, "DriftSteer": 1, "Steer": 1, "SlowDownSpd": 80, "Daze": -10, "UltCharge": -20, "SlipStreamSpd": 6.5, "SlipTime": 1.5, "TrickSpd": 2.5}},
    ],
}

@st.cache_data(show_spinner=False)
def df_from_category(category, stat_keys):
    rows = []
    for item in PARTS_DATABASE.get(category, []):
        row = {"name": item.get("name", "")}
        stats = item.get("stats", {}) or {}
        for k in stat_keys:
            row[k] = float(stats.get(k, 0.0))
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        df = pd.DataFrame(columns=["name"] + list(stat_keys))
    return df
