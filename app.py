import pandas as pd
import streamlit as st

st.set_page_config(page_title="U.S. Labor Market Dashboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "bls_labor_data.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df

df = load_data()

SERIES_META = {
    "Total Nonfarm Employment (000s)": "CES0000000001",
    "Unemployment Rate (%)": "LNS14000000",
    "Avg Hourly Earnings, Total Private ($)": "CES0500000003",
    "Labor Force Participation Rate (%)": "LNS11300000",
    "Manufacturing Employment (000s)": "CES3000000001",
    "Leisure & Hospitality Employment (000s)": "CES7000000001",
}

st.title("U.S. Labor Market Dashboard")
st.caption("Source: U.S. Bureau of Labor Statistics")

min_date = df["date"].min()
max_date = df["date"].max()

with st.sidebar:
    st.header("Filters")
    date_range = st.slider("Select date range", min_date, max_date, (min_date, max_date))

    indicators = st.multiselect(
        "Select indicators",
        list(SERIES_META.keys()),
        default=["Total Nonfarm Employment (000s)", "Unemployment Rate (%)"],
    )

mask = (df["date"] >= date_range[0]) & (df["date"] <= date_range[1])
df_range = df[mask]

st.subheader("Trends Over Time")

plot_data = []
for name in indicators:
    sid = SERIES_META[name]
    temp = df_range[df_range["series_id"] == sid][["date", "value"]]
    temp = temp.rename(columns={"value": name})
    plot_data.append(temp)

if plot_data:
    from functools import reduce
    chart_df = reduce(lambda left, right: pd.merge(left, right, on="date", how="outer"), plot_data)
    chart_df = chart_df.set_index("date")
    st.line_chart(chart_df)

st.caption(f"Last updated: {df['date'].max().strftime('%B %Y')}")
