"""
Used Car Market — Instrument Cluster
Streamlit + Plotly Express dashboard.

Run with:
    pip install streamlit plotly pandas openpyxl
    streamlit run app.py
"""

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from location_coords import LOCATION_COORDS

# ----------------------------------------------------------------------------
# Page config + theme
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Used Car Market Cluster",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BG        = "#12161B"
PANEL     = "#1A2028"
PANEL_ALT = "#1F2731"
BORDER    = "#2B3440"
AMBER     = "#FFB020"
TEAL      = "#35D0BA"
RED       = "#FF5C5C"
BLUE      = "#5FA8FF"
PURPLE    = "#B58AFF"
PINK      = "#FF7BAC"
TEXT      = "#EDF1F5"
MUTED     = "#8B96A3"
GRIDLINE  = "rgba(255,255,255,0.06)"

PALETTE = [AMBER, TEAL, BLUE, PURPLE, PINK, RED, "#7FD858", "#E8C468"]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"]  {{
    font-family: 'Inter', sans-serif;
}}
.stApp {{
    background:
      radial-gradient(ellipse 900px 500px at 15% -10%, rgba(255,176,32,0.06), transparent 60%),
      radial-gradient(ellipse 700px 500px at 100% 0%, rgba(53,208,186,0.05), transparent 60%),
      {BG};
    color: {TEXT};
}}
#MainMenu, footer, header {{ visibility: hidden; }}

.nameplate {{
    font-family: 'Chakra Petch', sans-serif;
    font-weight: 700;
    letter-spacing: 0.5px;
    font-size: 26px;
    text-transform: uppercase;
    color: {TEXT};
    margin-bottom: 0px;
}}
.nameplate span.sub {{
    display:block;
    font-family: 'Chakra Petch', sans-serif;
    font-size: 12px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: {MUTED};
    font-weight: 500;
    margin-top: 2px;
}}
.dot {{
    display:inline-block; width:10px; height:10px; border-radius:50%;
    background:{AMBER}; box-shadow:0 0 12px 2px rgba(255,176,32,0.35); margin-right:10px;
}}

.eyebrow {{
    font-family:'Chakra Petch', sans-serif; font-size:11px; letter-spacing:1.5px;
    text-transform:uppercase; color:{AMBER}; margin-bottom:2px;
}}
.panel-title {{ font-size:13px; color:{MUTED}; margin-bottom:10px; }}

.gauge-label {{
    text-align:center; font-family:'Chakra Petch',sans-serif; font-size:11px;
    letter-spacing:1.5px; text-transform:uppercase; color:{MUTED}; margin-top:-14px;
}}

div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    padding: 4px;
}}

/* selectboxes */
div[data-baseweb="select"] > div {{
    background:{PANEL_ALT} !important; border:1px solid {BORDER} !important;
    border-radius:6px !important; color:{TEXT} !important;
}}
label {{
    font-family:'Chakra Petch',sans-serif !important; font-size:10.5px !important;
    letter-spacing:1.2px !important; text-transform:uppercase !important; color:{MUTED} !important;
}}

/* buttons */
.stButton>button {{
    background:transparent; color:{MUTED}; border:1px solid {BORDER}; border-radius:6px;
    font-family:'Chakra Petch',sans-serif; font-size:11px; letter-spacing:1px; text-transform:uppercase;
}}
.stButton>button:hover {{ border-color:{RED}; color:{RED}; }}

hr {{ border-color:{BORDER}; }}

/* dataframe */
[data-testid="stDataFrame"] {{ border:1px solid {BORDER}; border-radius:8px; }}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path_or_buffer):
    df = pd.read_excel(path_or_buffer)
    df["km"] = (
        df["Kilometers Driven"].astype(str)
        .str.replace(" km", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float)
    )
    out = df[[
        "Brand", "Model", "Price", "Year", "km", "Fuel Type", "Transmission",
        "Location", "Owner", "Seller Type", "Drivetrain", "Seating Capacity"
    ]].copy()
    out.columns = [
        "brand", "model", "price", "year", "km", "fuel", "trans",
        "loc", "owner", "seller", "drive", "seats"
    ]
    return out


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "car_details_fixed.xlsx")

if os.path.exists(DEFAULT_PATH):
    RAW = load_data(DEFAULT_PATH)
else:
    uploaded = st.file_uploader("Upload car_details_fixed.xlsx to begin", type=["xlsx"])
    if uploaded is None:
        st.stop()
    RAW = load_data(uploaded)


# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(
        f'<div class="nameplate"><span class="dot"></span>Used Car Market Cluster'
        f'<span class="sub">India · Listings Analytics</span></div>',
        unsafe_allow_html=True,
    )
with h2:
    st.write("")

st.write("")

# ----------------------------------------------------------------------------
# Filter console
# ----------------------------------------------------------------------------
OWNER_ORDER = ["First", "Second", "Third", "Fourth", "More Than 4", "UnRegistered Car"]

for key, default in [("f_brand", "All"), ("f_fuel", "All"), ("f_trans", "All"), ("f_owner", "All")]:
    if key not in st.session_state:
        st.session_state[key] = default

def reset_filters():
    st.session_state["f_brand"] = "All"
    st.session_state["f_fuel"] = "All"
    st.session_state["f_trans"] = "All"
    st.session_state["f_owner"] = "All"

brand_counts = RAW["brand"].value_counts()
brand_options = ["All"] + list(brand_counts.index)
fuel_options = ["All"] + sorted(RAW["fuel"].unique().tolist())
trans_options = ["All"] + sorted(RAW["trans"].unique().tolist())
owner_options = ["All"] + [o for o in OWNER_ORDER if o in RAW["owner"].unique()]

c1, c2, c3, c4, c5 = st.columns([1.4, 1.1, 1.1, 1.3, 0.8])
with c1:
    brand = st.selectbox("Brand", brand_options, key="f_brand",
                          format_func=lambda b: b if b == "All" else f"{b} ({brand_counts.get(b, 0)})")
with c2:
    fuel = st.selectbox("Fuel", fuel_options, key="f_fuel")
with c3:
    trans = st.selectbox("Transmission", trans_options, key="f_trans")
with c4:
    owner = st.selectbox("Owner", owner_options, key="f_owner")
with c5:
    st.write("")
    st.button("Reset filters", on_click=reset_filters)

data = RAW.copy()
if brand != "All":
    data = data[data["brand"] == brand]
if fuel != "All":
    data = data[data["fuel"] == fuel]
if trans != "All":
    data = data[data["trans"] == trans]
if owner != "All":
    data = data[data["owner"] == owner]

year_range_html = ""
if not data.empty:
    year_range_html = (
        f'  ·  model years <b style="color:{TEXT}">'
        f'{int(data.year.min())}–{int(data.year.max())}</b>'
    )

st.markdown(
    f'<div style="color:{MUTED};font-size:12px;margin:4px 0 10px;">'
    f'<b style="color:{TEXT}">{len(data):,}</b> listings in view'
    f'{year_range_html}'
    f'</div>',
    unsafe_allow_html=True,
)

if data.empty:
    st.warning("No listings match this filter combination — try Reset filters.")
    st.stop()


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def fmt_inr(n):
    if n >= 1e7:
        return f"₹{n/1e7:.2f}Cr"
    if n >= 1e5:
        return f"₹{n/1e5:.2f}L"
    if n >= 1e3:
        return f"₹{n/1e3:.0f}K"
    return f"₹{n:.0f}"


def base_layout(fig, height=280):
    fig.update_layout(
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font_color=MUTED,
        font_family="Inter, sans-serif",
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        hovermode="closest",
        hoverdistance=100,   # forgiving hover radius — no need to sit exactly on a point/bar
        hoverlabel=dict(bgcolor=PANEL_ALT, bordercolor=BORDER, font=dict(color=TEXT)),
    )
    fig.update_xaxes(gridcolor=GRIDLINE, zerolinecolor=GRIDLINE)
    fig.update_yaxes(gridcolor=GRIDLINE, zerolinecolor=GRIDLINE)
    return fig


def gauge(value, max_value, color, prefix="", suffix="", title=""):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"prefix": prefix,"suffix": suffix,"font": {"family": "Chakra Petch, sans-serif","size": 30,"color": TEXT}},
        gauge={
            "shape": "angular",
            "axis": {"range": [0, max_value], "visible": False},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": PANEL_ALT,
            "borderwidth": 0,
            "steps": [{"range": [0, max_value], "color": PANEL_ALT}],
        },
        domain={"x": [0, 1], "y": [0.12, 1]},
    ))
    fig.update_layout(
        paper_bgcolor=PANEL,
        font_color=TEXT,
        margin=dict(l=20, r=20, t=10, b=0),
        height=170,
    )
    return fig


# ----------------------------------------------------------------------------
# Instrument cluster (KPI gauges)
# ----------------------------------------------------------------------------
avg_price = data["price"].mean()
avg_km = data["km"].mean()
avg_age = 2026 - data["year"].mean()

g1, g2, g3, g4 = st.columns(4)
with g1:
    st.plotly_chart(gauge(len(data), len(RAW), AMBER), use_container_width=True, config={"displayModeBar": False})
    st.markdown('<div class="gauge-label">Fleet size in view</div>', unsafe_allow_html=True)
with g2:
    st.plotly_chart(gauge(avg_price, 3_500_000, TEAL, prefix="₹"),use_container_width=True,config={"displayModeBar": False})
    st.markdown(f'<div class="gauge-label">Avg. price · {fmt_inr(avg_price)}</div>', unsafe_allow_html=True)
with g3:
    st.plotly_chart(gauge(avg_km, 150_000, BLUE), use_container_width=True, config={"displayModeBar": False})
    st.markdown(f'<div class="gauge-label">Avg. km on clock</div>', unsafe_allow_html=True)
with g4:
    st.plotly_chart(gauge(avg_age, 20, PURPLE), use_container_width=True, config={"displayModeBar": False})
    st.markdown('<div class="gauge-label">Avg. age (years)</div>', unsafe_allow_html=True)

st.write("")

# ----------------------------------------------------------------------------
# Row 1: brand bubble + fuel donut
# ----------------------------------------------------------------------------
r1c1, r1c2 = st.columns([2, 1])

with r1c1:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Brand lineup</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Avg. asking price by top brands (bubble size = listings)</div>',
                     unsafe_allow_html=True)
        brand_agg = (
            data.groupby("brand")
            .agg(avg_price=("price", "mean"), count=("price", "size"))
            .sort_values("count", ascending=False)
            .head(15)
            .reset_index()
        )
        fig = px.scatter(
            brand_agg, x="brand", y="avg_price", size="count", color="brand",
            size_max=55, color_discrete_sequence=PALETTE,
            labels={"avg_price": "Avg. price", "brand": ""},
        )
        fig.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,0.3)")),
                           hovertemplate="<b>%{x}</b><br>Avg price: %{y:,.0f}<br>Listings: %{marker.size}<extra></extra>")
        fig.update_yaxes(tickprefix="₹")
        fig.update_layout(showlegend=False)
        base_layout(fig, height=320)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with r1c2:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Fuel mix</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Listings by fuel type</div>', unsafe_allow_html=True)
        fuel_agg = data["fuel"].value_counts().reset_index()
        fuel_agg.columns = ["fuel", "count"]
        fuel_agg = fuel_agg.sort_values("count")
        fuel_agg["pct"] = (fuel_agg["count"] / fuel_agg["count"].sum() * 100).round(1)
        fig = px.bar(fuel_agg, x="count", y="fuel", orientation="h",
                     color="fuel", color_discrete_sequence=PALETTE,
                     custom_data=["pct"])
        fig.update_traces(hovertemplate="<b>%{y}</b><br>Listings: %{x}<br>%{customdata[0]}%<extra></extra>")
        fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="")
        base_layout(fig, height=320)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ----------------------------------------------------------------------------
# Row 2: year trend + top cities
# ----------------------------------------------------------------------------
r2c1, r2c2 = st.columns(2)

with r2c1:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Model year trend</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Median price by manufacture year</div>', unsafe_allow_html=True)
        year_agg = data.groupby("year")["price"].median().reset_index().sort_values("year")
        fig = px.line(year_agg, x="year", y="price", markers=True,
                      color_discrete_sequence=[AMBER])
        fig.update_traces(fill="tozeroy", fillcolor="rgba(255,176,32,0.12)", line=dict(width=2.5))
        fig.update_yaxes(tickprefix="₹")
        base_layout(fig, height=280)
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with r2c2:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Where they\'re parked</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Top 10 listing cities</div>', unsafe_allow_html=True)
        city_agg = data["loc"].value_counts().head(10).reset_index()
        city_agg.columns = ["city", "count"]
        city_agg = city_agg.sort_values("count")
        fig = px.bar(city_agg, x="count", y="city", orientation="h",
                     color_discrete_sequence=[BLUE])
        base_layout(fig, height=280)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ----------------------------------------------------------------------------
# Region map — geographic spread with details
# ----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="eyebrow">Geographic spread</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Listings by region — bubble size = listings, color = avg. price</div>',
                 unsafe_allow_html=True)

    loc_agg = (
        data.groupby("loc")
        .agg(count=("price", "size"), avg_price=("price", "mean"), avg_km=("km", "mean"))
        .reset_index()
    )
    loc_agg["lat"] = loc_agg["loc"].map(lambda l: LOCATION_COORDS.get(l, (None, None))[0])
    loc_agg["lon"] = loc_agg["loc"].map(lambda l: LOCATION_COORDS.get(l, (None, None))[1])
    loc_agg = loc_agg.dropna(subset=["lat", "lon"])
    loc_agg["avg_price_fmt"] = loc_agg["avg_price"].map(fmt_inr)
    loc_agg["avg_km_fmt"] = loc_agg["avg_km"].map(lambda x: f"{x:,.0f} km")

    map_col, table_col = st.columns([2.2, 1])

    with map_col:
        fig = px.scatter_mapbox(
            loc_agg, lat="lat", lon="lon",
            size="count", color="avg_price",
            hover_name="loc",
            custom_data=["count", "avg_price_fmt", "avg_km_fmt"],
            size_max=42, zoom=3.5, center={"lat": 22.9, "lon": 79.5},
            color_continuous_scale=[[0, BLUE], [0.5, AMBER], [1, RED]],
            mapbox_style="carto-darkmatter",
        )
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>"
                          "Listings: %{customdata[0]}<br>"
                          "Avg. price: %{customdata[1]}<br>"
                          "Avg. km: %{customdata[2]}<extra></extra>"
        )
        fig.update_layout(
            paper_bgcolor=PANEL,
            margin=dict(l=0, r=0, t=0, b=0),
            height=440,
            hoverdistance=40,
            coloraxis_colorbar=dict(title="Avg. price", tickprefix="₹", len=0.8),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with table_col:
        region_table = (
            loc_agg[["loc", "count", "avg_price_fmt", "avg_km_fmt"]]
            .sort_values("count", ascending=False)
            .head(12)
            .rename(columns={"loc": "City", "count": "Listings",
                              "avg_price_fmt": "Avg. price", "avg_km_fmt": "Avg. km"})
        )
        st.dataframe(region_table, use_container_width=True, hide_index=True, height=440)

# ----------------------------------------------------------------------------
# Row 3: transmission + owner + price band
# ----------------------------------------------------------------------------
r3c1, r3c2, r3c3 = st.columns(3)

with r3c1:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Gearbox</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Manual vs. automatic</div>', unsafe_allow_html=True)
        trans_agg = data["trans"].value_counts().reset_index()
        trans_agg.columns = ["trans", "count"]
        fig = px.pie(trans_agg, names="trans", values="count", hole=0.62,
                     color_discrete_sequence=[BLUE, TEAL])
        fig.update_traces(textinfo="percent", textfont_color=TEXT,
                           marker=dict(line=dict(color=PANEL, width=2)))
        fig.update_layout(legend=dict(orientation="h", y=-0.15, font=dict(size=10)))
        base_layout(fig, height=260)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with r3c2:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Ownership history</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Number of previous owners</div>', unsafe_allow_html=True)
        owner_agg = data["owner"].value_counts().reindex(
            [o for o in OWNER_ORDER if o in data["owner"].unique()]
        ).reset_index()
        owner_agg.columns = ["owner", "count"]
        fig = px.bar(owner_agg, x="owner", y="count", color_discrete_sequence=[PURPLE])
        base_layout(fig, height=260)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with r3c3:
    with st.container(border=True):
        st.markdown('<div class="eyebrow">Price band</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Listings by price range</div>', unsafe_allow_html=True)
        bins = [0, 300000, 600000, 1000000, 2000000, 5000000, np.inf]
        labels = ["<3L", "3-6L", "6-10L", "10-20L", "20-50L", "50L+"]
        band = pd.cut(data["price"], bins=bins, labels=labels, right=False)
        band_agg = band.value_counts().reindex(labels).reset_index()
        band_agg.columns = ["band", "count"]
        fig = px.bar(band_agg, x="band", y="count", color_discrete_sequence=[AMBER])
        base_layout(fig, height=260)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ----------------------------------------------------------------------------
# Showroom floor table
# ----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown('<div class="eyebrow">Showroom floor</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Top 10 most expensive listings in view</div>', unsafe_allow_html=True)
    top10 = data.sort_values("price", ascending=False).head(10)[
        ["brand", "model", "year", "fuel", "trans", "loc", "km", "owner", "price"]
    ].copy()
    top10["km"] = top10["km"].map(lambda x: f"{x:,.0f} km")
    top10["price"] = top10["price"].map(fmt_inr)
    top10.columns = ["Brand", "Model", "Year", "Fuel", "Gearbox", "City", "Km driven", "Owner", "Price"]
    st.dataframe(top10, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# Download full dataset
# ----------------------------------------------------------------------------
with st.container(border=True):
    st.markdown(
        '<div class="eyebrow">Dataset</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="panel-title">Download the original dataset</div>',
        unsafe_allow_html=True,
    )

    with open(DEFAULT_PATH, "rb") as file:
        st.download_button(
            label="📥 Download Original Dataset",
            data=file,
            file_name="car_details_fixed.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

st.markdown(
    f'<div style="text-align:center;color:{MUTED};font-size:11.5px;margin-top:20px;">'
    f'Dataset: 2,059 used-car listings across India · Built for exploratory analysis, not a valuation tool</div>',
    unsafe_allow_html=True,
)