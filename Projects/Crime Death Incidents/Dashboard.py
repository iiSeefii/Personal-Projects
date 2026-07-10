import pandas as pd
import os
import re
import plotly.express as px
import streamlit as st

st.set_page_config(page_title=' Dashboard', page_icon='', layout='wide', initial_sidebar_state='expanded')

st.title('Crime Death Incidents')
data = pd.read_excel(os.path.join(os.path.dirname(__file__), "crime_data.xlsx"))

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

# =============== CHARTS ===============
fig1 = px.pie(filtered_data, names='SHIFT', template='plotly_dark')
fig1.update_traces(textinfo='label+value+percent')

df2 = filtered_data.groupby(['OFFENSE', 'METHOD'])['METHOD'].count().reset_index(name='COUNT')
fig2 = px.bar(df2, x='OFFENSE', y='COUNT', color='METHOD', template='plotly_dark')

fig3 = px.histogram(filtered_data, x='REPORTING_GAP', template='plotly_dark')

fig4 = px.line(filtered_data, x='OFFENSE', y=filtered_data['INCIDENT_DURATION'].apply(convert_to_hours_as_nums), template='plotly_dark')

fig5 = px.pie(filtered_data, names='DISTRICT', hole=0.4, template='plotly_dark')

fig6 = px.line(filtered_data.sort_values('VOTING_PRECINCT'), x='VOTING_PRECINCT', y='OFFENSE', color='VOTING_PRECINCT', template='plotly_dark')

fig7 = px.pie(filtered_data, names='OFFENSE', values=filtered_data['INCIDENT_DURATION'].apply(convert_to_hours_as_nums), template='plotly_dark')

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
