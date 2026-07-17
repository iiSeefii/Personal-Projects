import pandas as pd
import os
import re
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Dashboard', page_icon='', layout='wide', initial_sidebar_state='expanded')

st.title('Crime Death Incidents')
data = pd.read_excel(os.path.join(os.path.dirname(__file__), "crime_data_cleaned.xlsx"))

def convert_to_hours_as_nums(x):
    if x is None:
        return 0
    h = 0
    m = 0
    if 'H' in str(x):
        h = int(str(x).split('H')[0])
        x = str(x).split('H')[1]
    if 'M' in str(x):
        m = int(str(x).replace('M', ''))
    return h + m / 60

data['NEIGHBORHOOD_CLUSTER'] = pd.Categorical(data['NEIGHBORHOOD_CLUSTER'], categories=sorted(data['NEIGHBORHOOD_CLUSTER'].dropna().unique(), key=lambda x: int(re.search(r'\d+', x).group())), ordered=True)
data['VOTING_PRECINCT'] = pd.Categorical(data['VOTING_PRECINCT'], categories=sorted(data['VOTING_PRECINCT'].dropna().unique(), key=lambda x: int(re.search(r'\d+', x).group())), ordered=True)
data = data.sort_values('NEIGHBORHOOD_CLUSTER')

# =============== FILTERS ===============
st.sidebar.title('Filters')
st.sidebar.markdown('---------')

ccn_search = st.sidebar.text_input('Search by CCN')
psa_filter = st.sidebar.multiselect('PSA', options=sorted(data['PSA'].dropna().unique().astype(int)))
block_filter = st.sidebar.multiselect('BLOCK', options=sorted(data['BLOCK'].dropna().unique()))
block_group_filter = st.sidebar.multiselect('BLOCK GROUP', options=sorted(data['BLOCK_GROUP-CENSUS_TRACT & WARD'].dropna().unique()))

filtered_data = data.copy()
if ccn_search:
    filtered_data = filtered_data[filtered_data['CCN'].astype(str).str.contains(ccn_search)]
if psa_filter:
    filtered_data = filtered_data[filtered_data['PSA'].isin(psa_filter)]
if block_filter:
    filtered_data = filtered_data[filtered_data['BLOCK'].isin(block_filter)]
if block_group_filter:
    filtered_data = filtered_data[filtered_data['BLOCK_GROUP-CENSUS_TRACT & WARD'].isin(block_group_filter)]

# helper column for duration in hours (compute once, reused)
filtered_data['DURATION_HOURS'] = filtered_data['INCIDENT_DURATION'].apply(convert_to_hours_as_nums)

# =============== CHART STYLING HELPER ===============
def style_chart(fig, height=430):
    fig.update_layout(
        template='plotly_dark',
        height=height,
        hovermode='x unified',   # shows clean detail box on hover instead of default crosshair
        dragmode=False,          # disables the "+" zoom-select cursor
        margin=dict(t=50, b=40, l=40, r=20),
    )
    return fig

# =============== CHARTS ===============
fig1 = px.pie(filtered_data, names='SHIFT', template='plotly_dark')
fig1.update_traces(textinfo='label+value+percent')
fig1 = style_chart(fig1)

df2 = filtered_data.groupby(['OFFENSE', 'METHOD'])['METHOD'].count().reset_index(name='COUNT')
fig2 = px.bar(df2, x='OFFENSE', y='COUNT', color='METHOD', template='plotly_dark')
fig2 = style_chart(fig2)

fig3 = px.histogram(filtered_data, x='REPORTING_GAP', template='plotly_dark')
fig3 = style_chart(fig3)

# ---- FIXED: average duration per offense, sorted, single connected line ----
df4 = (
    filtered_data.groupby('OFFENSE')['DURATION_HOURS']
    .mean()
    .reset_index()
    .sort_values('DURATION_HOURS', ascending=False)
)
fig4 = px.line(df4, x='OFFENSE', y='DURATION_HOURS', markers=True, template='plotly_dark')
fig4.update_traces(line=dict(width=3), marker=dict(size=9))
fig4.update_yaxes(title='Avg Duration (Hours)')
fig4 = style_chart(fig4)

fig5 = px.pie(filtered_data, names='DISTRICT', hole=0.4, template='plotly_dark')
fig5 = style_chart(fig5)

fig6 = px.line(filtered_data.sort_values('VOTING_PRECINCT'), x='VOTING_PRECINCT', y='OFFENSE', color='VOTING_PRECINCT', template='plotly_dark')
fig6 = style_chart(fig6)

fig7 = px.pie(filtered_data, names='OFFENSE', values=filtered_data['DURATION_HOURS'], template='plotly_dark')
fig7 = style_chart(fig7)

# =============== LAYOUT ===============
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig4, use_container_width=True)
with col2:
    st.plotly_chart(fig2, use_container_width=True)

st.plotly_chart(fig3, use_container_width=True)

col4, col5, col6 = st.columns(3)
with col4:
    st.plotly_chart(fig1, use_container_width=True)
with col5:
    st.plotly_chart(fig5, use_container_width=True)
with col6:
    st.plotly_chart(fig7, use_container_width=True)

st.plotly_chart(fig6, use_container_width=True)

with st.expander("Click To Expand Data"):
    st.dataframe(filtered_data)
