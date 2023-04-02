"""
Scripts related to fetching data
"""
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

URL_NSE_EQUITY = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
URL_NSE_REITS = "https://archives.nseindia.com/content/equities/REITS_L.csv"
URL_MF_DATA = "https://www.amfiindia.com/spages/NAVAll.txt"
FOLDER_DATA = "/Users/dex/Documents/Rohit/PythonProjects/GnuCashUtils/data"


def _fetch_data(data_type: str) -> pd.DataFrame:
    # Check if today's data is already available
    dt = datetime.now().strftime("%Y_%m_%d")
    if data_type not in ["EQ", "REIT"]:
        raise KeyError("Unknown data type. Available data types: EQ, REIT")
    Path(f"{FOLDER_DATA}/{data_type}").mkdir(parents=True, exist_ok=True)
    dt = f"{FOLDER_DATA}/{data_type}/{dt}_{data_type}_L.csv"
    if os.path.exists(dt):
        df = pd.read_csv(dt)
        df.columns = [x.strip() for x in df.columns]
        return df

    if data_type == "EQ":
        current_url = URL_NSE_EQUITY
    elif data_type == "REIT":
        current_url = URL_NSE_REITS
    else:
        raise KeyError("Unknown data type")
    response = requests.get(current_url)
    if response.status_code == 200:
        with open(dt, "wb") as f:
            f.write(response.content)
    else:
        raise ValueError(f"Unable to fetch Equity Data from {current_url}")

    df = pd.read_csv(dt)
    df.columns = [x.strip() for x in df.columns]
    return df


def get_eq_data():
    return _fetch_data("EQ")


def get_reit_data():
    return _fetch_data("REIT")


def get_mf_data():
    # Check if today's data is already available
    dt = datetime.now().strftime("%Y_%m_%d")
    Path(f"{FOLDER_DATA}/MF").mkdir(parents=True, exist_ok=True)
    dt = f"{FOLDER_DATA}/MF/{dt}_NAV.csv"
    if os.path.exists(dt):
        df = pd.read_csv(dt)
        return df

    response = requests.get(URL_MF_DATA)
    rows = []
    if response.status_code == 200:
        for line in response.text.split("\n"):
            if len(line.strip()) == 0:
                continue
            line = line.strip().split(";")
            if len(line) != 6:
                continue
            rows.append(line)
    else:
        raise ValueError(f"Unable to fetch MF Data from {URL_MF_DATA}")

    headers = rows[0]
    headers = [x.strip() for x in headers]
    rows = rows[1:]
    df = pd.DataFrame(rows, columns=headers)
    df.to_csv(dt, index=False)
    return df


def run():
    # eq_df = get_eq_data()
    mf_df = get_mf_data()
    print(mf_df[["Scheme Name", "ISIN Div Payout/ ISIN Growth", "Net Asset Value"]])
