import os
import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_PATH = os.path.join(DATA_DIR, "bls_labor_data.csv")

st.set_page_config(page_title="U.S. Labor Market Dashboard", layout="wide")

st.write("Base directory contents:")
st.write(os.listdir(BASE_DIR))

st.write("Data directory contents:")
if os.path.exists(DATA_DIR):
    st.write(os.listdir(DATA_DIR))
else:
    st.error("Data directory does not exist")

st.write("Full CSV path:")
st.write(DATA_PATH)

if not os.path.exists(DATA_PATH):
    st.error("CSV file NOT found at runtime")
    st.stop()

df = pd.read_csv(DATA_PATH, parse_dates=["date"])

st.success("CSV file loaded successfully!")
st.dataframe(df)
