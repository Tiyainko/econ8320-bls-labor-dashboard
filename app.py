import os
import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(page_title="U.S. Labor Market Dashboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "bls_labor_data.csv")

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"CSV file not found at: {DATA_PATH}")
        st.stop()
    df = pd.read_csv(DATA_PATH, parse_dates=["date"])
    return df

df = load_data()

st.title("U.S. Labor Market Dashboard (BLS)")
st.caption("Source: U.S. Bureau of Labor Statistics")

series_options = df["series_name"].unique()
selected_series = st.sidebar.selectbox("Select Economic Indicator:", series_options)

filtered_df = df[df["series_name"] == selected_series]
filtered_df = filtered_df.sort_values("date")

latest_value = filtered_df.iloc[-1]["value"]
latest_date = filtered_df.iloc[-1]["date"]

if len(filtered_df) > 1:
    prev_value = filtered_df.iloc[-2]["value"]
    change = latest_value - prev_value
    pct_change = (change / prev_value) * 100
else:
    change = 0
    pct_change = 0

col1, col2, col3 = st.columns(3)

col1.metric(
    label="Current Value",
    value=f"{latest_value:,.0f}")

col2.metric(
    label="Month-over-Month Change",
    value=f"{change:,.0f}")

col3.metric(
    label="Percent Change",
    value=f"{pct_change:.2f}%")

if change > 0:
    direction = "increased"
elif change < 0:
    direction = "decreased"
else:
    direction = "remained unchanged"

st.info(
    f"📘 Interpretation: Between last month and the latest release, "
    f"**{selected_series} {direction} by {abs(change):,.0f} units "
    f"({pct_change:.2f}%)**, suggesting a "
    f"{'strengthening' if change > 0 else 'weakening' if change < 0 else 'stable'} labor market trend.")


chart = (
    alt.Chart(filtered_df)
    .mark_line(point=True)
    .encode(
        x="date:T",
        y="value:Q",
        tooltip=["date:T", "value:Q"])
    .properties(title=selected_series))

st.altair_chart(chart, use_container_width=True)

with st.expander("View Raw Data"):
    st.dataframe(filtered_df)

st.caption(f"Last updated: {df['date'].max().date()}")
