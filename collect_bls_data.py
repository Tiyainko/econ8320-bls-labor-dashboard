import requests
import pandas as pd
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "bls_labor_data.csv")

START_YEAR = 2010
END_YEAR = datetime.now().year

SERIES = {
    "CES0000000001": "Total Nonfarm Employment",
    "LNS14000000": "Unemployment Rate"}

os.makedirs(DATA_DIR, exist_ok=True)

rows = []

for series_id, series_name in SERIES.items():
    for year in range(START_YEAR, END_YEAR + 1):
        url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/{series_id}"
        params = {
            "startyear": year,
            "endyear": year}

        response = requests.get(url, params=params)
        data = response.json()

        if "Results" not in data:
            print(f"Failed for {series_id} {year}")
            continue

        for item in data["Results"]["series"][0]["data"]:
            period = item["period"]
            if period == "M13":  
                continue

            month = int(period.replace("M", ""))
            date = datetime(year, month, 1)

            rows.append({
                "series_id": series_id,
                "series_name": series_name,
                "year": year,
                "period": period,
                "period_name": item["periodName"],
                "value": float(item["value"]),
                "date": date})

df = pd.DataFrame(rows)
df = df.sort_values(["series_name", "date"])
df.to_csv(OUTPUT_FILE, index=False)

print(f"Full BLS history saved to {OUTPUT_FILE}")
