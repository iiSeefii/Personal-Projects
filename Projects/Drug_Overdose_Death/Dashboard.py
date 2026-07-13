import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from pathlib import Path

# ---------------- Page Config ----------------
st.set_page_config(page_title="Drug Dashboard", layout='wide', initial_sidebar_state='expanded')

# ---------------- Read Data ----------------
BASE_DIR = Path(__file__).resolve().parent
excel_file = BASE_DIR / "Drug_data_cleaned.xlsx"
data = pd.read_excel(excel_file)

st.title("Drug Dashboard")

# ====================================================
# Filter
# ====================================================

st.sidebar.header("Filters")

selected_id = st.sidebar.selectbox(
    "Select ID",
    sorted(data["ID"].unique())
)
st.sidebar.markdown('---------')
filtered_data = data[data["ID"] == selected_id]

# ====================================================
# Metrics
# ====================================================

with st.container(border=True):
    st.subheader("Dataset Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Gender", filtered_data["GENDER"].iloc[0])

    with col2:
        st.metric("Panel", filtered_data["PANEL"].iloc[0])

    with col3:
        st.metric("Year", filtered_data["YEAR"].iloc[0])

# ====================================================
# Bar Chart
# ====================================================

cnt_fig1 = (
    filtered_data.groupby(["GENDER", "AGE-GROUP"])
    .size()
    .reset_index(name="Count")
)

fig1 = px.bar(
    cnt_fig1,
    x="Count",
    y="GENDER",
    color="AGE-GROUP",
    orientation="h",
    template="plotly_dark",
    title="Gender Distribution by Age Group"
)

fig1.update_layout(barmode="stack")

# ====================================================
# Line Chart
# ====================================================

yearly = (
    filtered_data.groupby("YEAR")["ESTIMATE"]
    .agg(Max="max", Average="mean")
    .reset_index()
)

fig2 = go.Figure()

fig2.add_trace(
    go.Scatter(
        x=yearly["YEAR"],
        y=yearly["Max"],
        mode="lines+markers",
        name="Max Estimate"
    )
)

fig2.add_trace(
    go.Scatter(
        x=yearly["YEAR"],
        y=yearly["Average"],
        mode="lines+markers",
        name="Average Estimate"
    )
)

fig2.update_layout(
    title="Max vs Average Estimate by Year",
    xaxis_title="Year",
    yaxis_title="Estimate",
    template="plotly_dark"
)

# ====================================================
# Race Chart
# ====================================================

chart = (
    filtered_data.groupby(["RACE", "STUB_NAME"])
    .size()
    .reset_index(name="Count")
)

fig3 = px.bar(
    chart,
    x="Count",
    y="RACE",
    color="STUB_NAME",
    orientation="h",
    barmode="stack",
    template="plotly_dark",
    title="Race by Stub Name"
)

# ====================================================
# Dashboard Layout
# ====================================================

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig1, use_container_width=True, key="fig1")

with col2:
    st.plotly_chart(fig2, use_container_width=True, key="fig2")

st.plotly_chart(fig3, use_container_width=True, key="fig3")
