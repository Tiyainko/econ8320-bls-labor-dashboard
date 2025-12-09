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

chart = (
    alt.Chart(filtered_df)
    .mark_line(point=True)
    .encode(
        x="date:T",
        y="value:Q",
        tooltip=["date:T", "value:Q"]
    )
    .properties(title=selected_series)
)

st.altair_chart(chart, use_container_width=True)

with st.expander("View Raw Data"):
    st.dataframe(filtered_df)

st.caption(f"Last updated: {df['date'].max().date()}")
