import requests
import pandas as pd
import os
from datetime import datetime

SERIES = {
    "CES0000000001": "Total Nonfarm Employment",
    "LNS14000000": "Unemployment Rate"}

START_YEAR = 2019
END_YEAR = datetime.now().year

OUT_PATH = os.path.join("data", "bls_labor_data.csv")

rows = []

for series_id, series_name in SERIES.items():
    url = f"https://api.bls.gov/publicAPI/v2/timeseries/data/{series_id}?startyear={START_YEAR}&endyear={END_YEAR}"

    response = requests.get(url)
    data = response.json()

    if "Results" not in data:
        raise RuntimeError("BLS API request failed.")

    for series in data["Results"]["series"]:
        for item in series["data"]:

            year = int(item["year"])
            period = item["period"]

            if not period.startswith("M"):
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
df = pd.DataFrame(rows).sort_values("date")

os.makedirs("data", exist_ok=True)
df.to_csv(OUT_PATH, index=False)

print("Real BLS data pulled successfully")
