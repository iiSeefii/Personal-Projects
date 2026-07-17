import os
import re
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="DC Crime Dashboard",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# STYLE
# =========================================================
st.markdown("""
<style>
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1f2937, #ef4444);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .subtitle { color: #6b7280; font-size: 1.05rem; margin-top: 0px; }
    div[data-testid="stMetric"] {
        background-color: rgba(148, 163, 184, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.25);
        padding: 15px 15px 10px 15px;
        border-radius: 12px;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        border-left: 5px solid #ef4444;
        padding-left: 10px;
        margin-top: 25px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATA LOADING
# =========================================================
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "crime_data_cleaned.xlsx")
    df = pd.read_excel(file_path)

    # Dates
    df["START_DATE"] = pd.to_datetime(df["START_DATE"], errors="coerce")
    df["REPORT_DAT"] = pd.to_datetime(df["REPORT_DAT"], errors="coerce")

    # Derived time fields
    df["DATE"] = df["START_DATE"].dt.date
    df["HOUR"] = df["START_DATE"].dt.hour
    df["DAY_NAME"] = df["START_DATE"].dt.day_name()
    df["MONTH"] = df["START_DATE"].dt.to_period("M").astype(str)

    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["DAY_NAME"] = pd.Categorical(df["DAY_NAME"], categories=day_order, ordered=True)

    # Parse "24H 5M" style durations into total hours (float)
    def parse_duration_to_hours(val):
        if pd.isna(val):
            return np.nan
        s = str(val)
        h_match = re.search(r"(-?\d+)H", s)
        m_match = re.search(r"(-?\d+)M", s)
        hours = int(h_match.group(1)) if h_match else 0
        minutes = int(m_match.group(1)) if m_match else 0
        return hours + minutes / 60

    df["DURATION_HRS"] = df["INCIDENT_DURATION"].apply(parse_duration_to_hours)
    df["REPORTING_GAP_HRS"] = df["REPORTING_GAP"].apply(parse_duration_to_hours)

    df["DISTRICT"] = df["DISTRICT"].apply(lambda x: f"District {int(x)}" if pd.notna(x) else "Unknown")
    df["NEIGHBORHOOD_CLUSTER"] = df["NEIGHBORHOOD_CLUSTER"].fillna("Unknown")

    return df

df = load_data()

# =========================================================
# HEADER
# =========================================================
st.markdown('<p class="main-title">🚨 DC Crime Incidents Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Interactive analysis of Washington, D.C. crime data — filter, explore, and uncover insights</p>', unsafe_allow_html=True)
st.divider()

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.header("🔎 Filters")

min_date, max_date = df["START_DATE"].min().date(), df["START_DATE"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = date_range
else:
    start_d, end_d = min_date, max_date

shift_opts = sorted(df["SHIFT"].dropna().unique())
shift_sel = st.sidebar.multiselect("Shift", shift_opts, default=shift_opts)

offense_opts = sorted(df["OFFENSE"].dropna().unique())
offense_sel = st.sidebar.multiselect("Offense Type", offense_opts, default=offense_opts)

method_opts = sorted(df["METHOD"].dropna().unique())
method_sel = st.sidebar.multiselect("Method Used", method_opts, default=method_opts)

district_opts = sorted(df["DISTRICT"].dropna().unique())
district_sel = st.sidebar.multiselect("District", district_opts, default=district_opts)

cluster_opts = sorted(df["NEIGHBORHOOD_CLUSTER"].dropna().unique(), key=lambda x: (len(x), x))
cluster_sel = st.sidebar.multiselect("Neighborhood Cluster", cluster_opts, default=cluster_opts)

st.sidebar.markdown("---")
st.sidebar.caption(f"📅 Data available from {min_date} to {max_date}")
st.sidebar.caption(f"📊 Total raw rows: {len(df):,}")

# Apply filters
mask = (
    (df["START_DATE"].dt.date >= start_d)
    & (df["START_DATE"].dt.date <= end_d)
    & (df["SHIFT"].isin(shift_sel))
    & (df["OFFENSE"].isin(offense_sel))
    & (df["METHOD"].isin(method_sel))
    & (df["DISTRICT"].isin(district_sel))
    & (df["NEIGHBORHOOD_CLUSTER"].isin(cluster_sel))
)
fdf = df[mask].copy()

if fdf.empty:
    st.warning("No data matches these filters. Try widening your selection.")
    st.stop()

# =========================================================
# KPI ROW
# =========================================================
total_incidents = len(fdf)
armed_pct = (fdf["METHOD"].isin(["GUN", "KNIFE"]).sum() / total_incidents * 100)
avg_report_gap = fdf["REPORTING_GAP_HRS"].median()
top_offense = fdf["OFFENSE"].value_counts().idxmax()
top_district = fdf["DISTRICT"].value_counts().idxmax()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Incidents", f"{total_incidents:,}")
k2.metric("Armed Crime Rate", f"{armed_pct:.1f}%", help="Incidents involving a firearm or a knife")
k3.metric("Median Reporting Gap (hrs)", f"{avg_report_gap:.1f}h", help="Median time between when an incident occurred and when it was reported")
k4.metric("Most Common Offense", top_offense)
k5.metric("Most Affected District", top_district)

st.divider()

# =========================================================
# ROW 1: Trend over time + Offense breakdown
# =========================================================
st.markdown('<p class="section-header">📈 Trend Over Time & Offense Types</p>', unsafe_allow_html=True)
c1, c2 = st.columns([2, 1])

with c1:
    trend = fdf.groupby("MONTH").size().reset_index(name="Incident Count")
    trend = trend.sort_values("MONTH")
    fig_trend = px.line(
        trend, x="MONTH", y="Incident Count", markers=True,
        title="Monthly Incident Count",
    )
    fig_trend.update_layout(xaxis_title="Month", yaxis_title="Incident Count", hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    offense_counts = fdf["OFFENSE"].value_counts().reset_index()
    offense_counts.columns = ["OFFENSE", "COUNT"]
    fig_offense = px.pie(
        offense_counts, names="OFFENSE", values="COUNT", hole=0.45,
        title="Offense Type Distribution",
    )
    fig_offense.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig_offense, use_container_width=True)

# =========================================================
# ROW 2: Shift & Method
# =========================================================
st.markdown('<p class="section-header">🕐 Timing & Method of Crime</p>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    shift_offense = fdf.groupby(["SHIFT", "OFFENSE"]).size().reset_index(name="COUNT")
    fig_shift = px.bar(
        shift_offense, x="SHIFT", y="COUNT", color="OFFENSE",
        title="Crimes by Shift and Offense Type", barmode="stack",
        category_orders={"SHIFT": ["DAY", "EVENING", "MIDNIGHT"]},
    )
    fig_shift.update_layout(xaxis_title="Shift", yaxis_title="Incident Count")
    st.plotly_chart(fig_shift, use_container_width=True)

with c4:
    dow_hour = fdf.groupby(["DAY_NAME", "HOUR"], observed=True).size().reset_index(name="COUNT")
    heat_pivot = dow_hour.pivot(index="DAY_NAME", columns="HOUR", values="COUNT").fillna(0)
    fig_heat = px.imshow(
        heat_pivot,
        labels=dict(x="Hour", y="Day", color="Incident Count"),
        aspect="auto", color_continuous_scale="Reds",
        title="Heatmap: Day × Hour",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# =========================================================
# ROW 3: Geography
# =========================================================
st.markdown('<p class="section-header">🗺️ Geographic Distribution</p>', unsafe_allow_html=True)
c5, c6 = st.columns([2, 1])

with c5:
    map_sample = fdf.dropna(subset=["LATITUDE", "LONGITUDE"])
    fig_map = px.scatter_mapbox(
        map_sample,
        lat="LATITUDE", lon="LONGITUDE",
        color="OFFENSE",
        hover_data=["DISTRICT", "SHIFT", "METHOD", "NEIGHBORHOOD_CLUSTER"],
        zoom=10.3, height=520,
        title="Incident Location Map",
    )
    fig_map.update_layout(mapbox_style="carto-positron", margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_map, use_container_width=True)

with c6:
    district_counts = fdf["DISTRICT"].value_counts().reset_index()
    district_counts.columns = ["DISTRICT", "COUNT"]
    district_counts = district_counts.sort_values("COUNT", ascending=True)
    fig_district = px.bar(
        district_counts, x="COUNT", y="DISTRICT", orientation="h",
        title="Incident Count by District", color="COUNT",
        color_continuous_scale="Reds",
    )
    fig_district.update_layout(xaxis_title="Incident Count", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(fig_district, use_container_width=True)

# =========================================================
# ROW 4: Neighborhood clusters + Method share
# =========================================================
st.markdown('<p class="section-header">🏘️ Neighborhood Clusters & Crime Method</p>', unsafe_allow_html=True)
c7, c8 = st.columns(2)

with c7:
    cluster_counts = fdf["NEIGHBORHOOD_CLUSTER"].value_counts().nlargest(10).reset_index()
    cluster_counts.columns = ["CLUSTER", "COUNT"]
    fig_cluster = px.bar(
        cluster_counts.sort_values("COUNT"), x="COUNT", y="CLUSTER", orientation="h",
        title="Top 10 Neighborhood Clusters by Incident Count", color="COUNT",
        color_continuous_scale="Oranges",
    )
    fig_cluster.update_layout(xaxis_title="Incident Count", yaxis_title="", coloraxis_showscale=False)
    st.plotly_chart(fig_cluster, use_container_width=True)

with c8:
    method_offense = fdf.groupby(["OFFENSE", "METHOD"]).size().reset_index(name="COUNT")
    fig_method = px.bar(
        method_offense, x="OFFENSE", y="COUNT", color="METHOD",
        title="Crime Method by Offense Type", barmode="stack",
    )
    fig_method.update_layout(xaxis_title="", yaxis_title="Incident Count", xaxis_tickangle=-30)
    st.plotly_chart(fig_method, use_container_width=True)

# =========================================================
# ROW 5: Duration & Reporting Gap
# =========================================================
st.markdown('<p class="section-header">⏱️ Incident Duration & Reporting Gap</p>', unsafe_allow_html=True)
c9, c10 = st.columns(2)

with c9:
    dur = fdf[fdf["DURATION_HRS"].between(0, 72)]  # trim extreme outliers for readability
    fig_dur = px.histogram(
        dur, x="DURATION_HRS", nbins=40, color="OFFENSE",
        title="Incident Duration Distribution (up to 72h)",
    )
    fig_dur.update_layout(xaxis_title="Duration (hours)", yaxis_title="Incident Count")
    st.plotly_chart(fig_dur, use_container_width=True)

with c10:
    gap = fdf[fdf["REPORTING_GAP_HRS"].between(0, 72)]
    fig_gap = px.box(
        gap, x="OFFENSE", y="REPORTING_GAP_HRS", color="OFFENSE",
        title="Reporting Gap by Offense Type (up to 72h)",
        points=False,
    )
    fig_gap.update_layout(xaxis_title="", yaxis_title="Reporting Gap (hours)", xaxis_tickangle=-30, showlegend=False)
    st.plotly_chart(fig_gap, use_container_width=True)

# =========================================================
# INSIGHTS
# =========================================================
st.markdown('<p class="section-header">💡 Quick Insights</p>', unsafe_allow_html=True)

peak_hour = fdf["HOUR"].value_counts().idxmax()
peak_day = fdf["DAY_NAME"].value_counts().idxmax()
slowest_report_offense = fdf.groupby("OFFENSE")["REPORTING_GAP_HRS"].median().idxmax()

insight_cols = st.columns(3)
insight_cols[0].info(f"🕑 Most incidents happen around **{peak_hour}:00**, and **{peak_day}** is the most frequent day.")
insight_cols[1].info(f"🔫 **{armed_pct:.1f}%** of incidents involved a weapon (firearm or knife).")
insight_cols[2].info(f"⏳ **{slowest_report_offense}** incidents take the longest to get reported compared to other offense types.")

# =========================================================
# RAW DATA
# =========================================================
with st.expander("📋 View Raw Data (filtered)"):
    st.dataframe(fdf.reset_index(drop=True), use_container_width=True)
    csv = fdf.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ Download Filtered Data (CSV)", csv, "filtered_crime_data.csv", "text/csv")

st.divider()
st.caption("Built by Seif | Streamlit + Plotly | DC Crime Incidents Dashboard")
