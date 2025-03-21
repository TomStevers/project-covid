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
    

    st.subheader("🗺️ COVID-19 Spread Over Time (Animated)")
    st.plotly_chart(plot_covid_spread_animation(), use_container_width=True)

    st.divider()

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

    # Create two columns for side-by-side layout
    col1, col2 = st.columns([1, 1])  # Adjust the ratio if needed

    # Sidebar selection
    available_countries = creating_available_countries()
    selected_country = st.sidebar.selectbox("Select a Country", available_countries)

    # Estimate parameters and fetch data
    r0_data = estimate_parameters(selected_country)

    # Display R0 Trajectory in the first column
    with col1:
        st.subheader("R₀ Over Time")
        fig_r0 = plot_R0_trajectory(r0_data, selected_country)
        if fig_r0:
            st.pyplot(fig_r0)
        else:
            st.error(f"No R₀ data available for {selected_country}.")

    # Display Death Rate Trajectory in the second column
    with col2:
        st.subheader("Death Rate Over Time")
        fig_death = plot_death_rate(r0_data, selected_country)
        if fig_death:
            st.pyplot(fig_death)
        else:
            st.error(f"No death rate data available for {selected_country}.")

with tab3:
    st.title("🇺🇸 USA Stats")
    # st.subheader("🗺️ COVID-19 Cases by State")
    st.plotly_chart(plot_usa_choropleth(connection), use_container_width=True) 

    col1, col2 = st.columns([1, 1])
                            

    with col1:
        st.plotly_chart(plot_confirmed_cases_map(connection))


    with col2:
        st.plotly_chart(plot_deaths_map(connection))

    
    st.divider()

    col3, col4 = st.columns([1, 1])

    with col3:
        st.subheader("US States with most confirmed cases")
        top_x_confirmed = get_top_x_data(connection, 'Confirmed')[["Admin2" , "Total"]]
        top_x_confirmed = top_x_confirmed.rename(columns={"Admin2": "County", "Total": "Confirmed Cases"})
        st.dataframe(top_x_confirmed, use_container_width=True, hide_index=True)

    with col4:
        st.subheader("US States with most Deaths")
        top_x_deaths = get_top_x_data(connection, 'Deaths')[["Admin2", "Total"]]
        top_x_deaths = top_x_deaths.rename(columns={"Admin2": "County", "Total": "Deaths"})
        st.dataframe(top_x_deaths, use_container_width=True, hide_index=True)

