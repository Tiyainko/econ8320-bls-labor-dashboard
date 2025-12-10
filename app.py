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
filtered_df = filtered_df.sort_values("date").reset_index(drop=True)

min_date = filtered_df["date"].min()
max_date = filtered_df["date"].max()

date_range = st.sidebar.slider(
    "Select Date Range:",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=(min_date.to_pydatetime(), max_date.to_pydatetime()))

filtered_df = filtered_df[
    (filtered_df["date"] >= date_range[0]) &
    (filtered_df["date"] <= date_range[1])]

filtered_df = filtered_df.sort_values("date").reset_index(drop=True)


latest_value = filtered_df.iloc[-1]["value"]
latest_date = filtered_df.iloc[-1]["date"]

if len(filtered_df) > 1:
    prev_value = filtered_df.iloc[-2]["value"]
    change = latest_value - prev_value
    pct_change = (change / prev_value) * 100
else:
    change = 0
    pct_change = 0

if "Rate" in selected_series or "Unemployment" in selected_series:
    display_value = f"{latest_value:.2f}%"
else:
    display_value = f"{latest_value:,.2f}"

col1, col2, col3 = st.columns(3)

col1.metric(label="Current Value", value=display_value)
col2.metric(label="Month-over-Month Change", value=f"{change:,.2f}")
col3.metric(label="Percent Change", value=f"{pct_change:.2f}%")

if change > 0:
    direction = "increased"
elif change < 0:
    direction = "decreased"
else:
    direction = "remained unchanged"

st.info(
    f"Interpretation: From **{filtered_df.iloc[-2]['date'].strftime('%B %Y')} "
    f"to {latest_date.strftime('%B %Y')}**, "
    f"**{selected_series} {direction} by {abs(change):,.2f} units "
    f"({pct_change:.2f}%)**, suggesting a "
    f"{'strengthening' if change > 0 else 'weakening' if change < 0 else 'stable'} labor market trend.")


chart = (
    alt.Chart(filtered_df)
    .mark_line(point=True)
    .encode(
        x=alt.X("date:T", title="Month", axis=alt.Axis(format="%b %Y")),
        y=alt.Y("value:Q", title="Value"),
        tooltip=[
            alt.Tooltip("date:T", title="Date", format="%B %Y"),
            alt.Tooltip("value:Q", title="Value")])
    .properties(title=selected_series))

st.altair_chart(chart, use_container_width=True)

with st.expander("View Raw Data"):
    st.dataframe(filtered_df)

st.caption(f"Last updated: {df['date'].max().date()}")

st.subheader("Sectoral Job Changes (Latest Month)")

sector_list = [
    "Manufacturing Employment",
    "Leisure & Hospitality Employment",
    "Total Nonfarm Employment"]

sector_df = df[df["series_name"].isin(sector_list)].copy()
sector_df = sector_df.sort_values(["series_name", "date"])

sector_df["prev_value"] = sector_df.groupby("series_name")["value"].shift(1)
sector_df["mo_change"] = sector_df["value"] - sector_df["prev_value"]

latest_sector_changes = sector_df.groupby("series_name").tail(1)

bar_chart = (
    alt.Chart(latest_sector_changes)
    .mark_bar()
    .encode(
        x=alt.X("series_name:N", title="Sector"),
        y=alt.Y("mo_change:Q", title="Month-to-Month Change"),
        tooltip=["series_name", "mo_change"])
    .properties(title="Latest Monthly Job Change by Sector"))

st.altair_chart(bar_chart, use_container_width=True)

st.subheader("Sector Employment Trends Over Time")

area_chart = (
    alt.Chart(sector_df)
    .mark_area(opacity=0.6)
    .encode(
        x=alt.X("date:T", title="Month"),
        y=alt.Y("value:Q", title="Employment Level"),
        color="series_name:N",
        tooltip=["series_name", "date:T", "value:Q"]
    )
    .properties(title="Employment Trends by Sector"))

st.altair_chart(area_chart, use_container_width=True)

