import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from covid_statistics_usa import *
from covid_sird_model import *
import covid_statistics as gs
from covid_statistics import *
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="COVID-19 Dashboard", layout="wide")

# Title
st.title("🦠 COVID-19 Dashboard")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Global Data", "SIRD Model", "USA Stats"])

with tab1:
    # Sidebar 
    st.sidebar.header("Select Date Range")
    start_date = st.sidebar.date_input("Start Date", datetime(2020, 1, 22))
    end_date = st.sidebar.date_input("End Date", datetime(2020, 7, 27))
    continent = st.sidebar.selectbox("Select Continent", ["All", "Asia", "Europe", "Africa", "North America", "South America", "Australia/Oceania"])

    # Convert selected dates to string format for SQL usage
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    # Get totals (Fix: Create new connection inside each function)
    total_active, total_deaths, total_recovered, total_confirmed = get_totals(start_date, end_date)
    top_cases_df = top_countries_by_cases()
    top_deaths_df = top_countries_by_deathrate()

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("🌍 Continent Map")
        st.plotly_chart(plot_continent_map(continent), use_container_width=True)

    with col2:
        st.subheader("🌎 Global Stats")
        st.metric(label="Total Active Cases", value=total_active)
        st.metric(label="Total Deaths", value=total_deaths)
        st.metric(label="Total Recovered", value=total_recovered)
        st.metric(label="Total Confirmed", value=total_confirmed)
    
    # Full-width graph
    st.subheader("📊 COVID-19 Trends")
    st.pyplot(plot_totals(start_date, end_date), use_container_width=True)

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("🔝 Most Cases")
        st.dataframe(top_cases_df, use_container_width=True, hide_index=True)
        
    with col4:
        st.subheader("⚰️ Most Deaths")
        st.dataframe(top_deaths_df, use_container_width=True, hide_index=True)

with tab2:
    st.title("📈 SIRD Model")
    st.write("Content for the SIRD Model will be added here.")

with tab3:
    st.title("🇺🇸 USA Stats")
    st.subheader("🗺️ COVID-19 Cases by State")
    st.plotly_chart(plot_usa_choropleth(connection), use_container_width=True) 
