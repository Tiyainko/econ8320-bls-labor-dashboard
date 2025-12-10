import requests
import pandas as pd
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "bls_labor_data.csv")

START_YEAR = 2019
END_YEAR = datetime.now().year

SERIES = {
    "CES0000000001": "Total Nonfarm Employment",
    "LNS14000000": "Unemployment Rate",
    "CES0500000003": "Average Hourly Earnings",
    "LNS11300000": "Labor Force Participation Rate",
    "CES3000000001": "Manufacturing Employment",
    "CES7000000001": "Leisure & Hospitality Employment"}


def fetch_series(series_id, series_name):
    url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/{series_id}?startyear={START_YEAR}&endyear={END_YEAR}"
    response = requests.get(url)
    data = response.json()

    if "Results" not in data or "series" not in data["Results"]:
        raise RuntimeError(f"BLS API failed for series: {series_id}")

    records = []
    for item in data["Results"]["series"][0]["data"]:
        if item["period"].startswith("M"):
            date_str = f'{item["year"]}-{item["period"][1:]}-01'
            records.append({
                "series_id": series_id,
                "series_name": series_name,
                "year": int(item["year"]),
                "period": item["period"],
                "period_name": item["periodName"],
                "value": float(item["value"]),
                "date": pd.to_datetime(date_str)})

    return records


all_data = []

for sid, name in SERIES.items():
    print(f"Fetching: {name}")
    all_data.extend(fetch_series(sid, name))

df_new = pd.DataFrame(all_data)


os.makedirs(DATA_DIR, exist_ok=True)

if os.path.exists(DATA_PATH):
    df_old = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df_final = pd.concat([df_old, df_new]).drop_duplicates(
        subset=["series_id", "date"], keep="last")
else:
    df_final = df_new

df_final = df_final.sort_values(["series_name", "date"])
df_final.to_csv(DATA_PATH, index=False)

print("Full monthly BLS data updated successfully.")
