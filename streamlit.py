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
st.title("COVID-19 Dashboard")

# Create tabs
tab1, tab2, tab3 = st.tabs(["Global Statistics", "SIRD Model", "USA Statistics"])

with tab1:
    # Sidebar 
    st.sidebar.header("Global Statistics")
    st.sidebar.subheader("Select Date Range")
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
        st.subheader("Total Cases Map", help = "Select a continent in the sidebar to view the total infections per selected continent")
        st.plotly_chart(plot_continent_map(continent), use_container_width=True)

    with col2:
        st.subheader("Global Statistics", help = "Select a begin date and an end date in the sidebar to view the global statistics for the selected date range")
        col2.metric("Total Active", f"{total_active:,}", delta=None)
        col2.metric("Total Deaths", f"{total_deaths:,}", delta=None)
        col2.metric("Total Recovered", f"{total_recovered:,}", delta=None)
        col2.metric("Total Confirmed", f"{total_confirmed:,}", delta=None)
    

    st.subheader("COVID-19 Spread Over Time (Animated)", help = "Press the play button to start the animation of the Covid-19 spread")
    st.plotly_chart(plot_covid_spread_animation(), use_container_width=True)

    st.divider()

    # Full-width graph
    st.subheader("COVID-19 Trends", help = "Select a begin date and an end date in the sidebar to view the global statistics plot for the selected date range")
    st.pyplot(plot_totals(start_date, end_date), use_container_width=True)

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Highest Infection Rate", help = "The infection rate is calculated by dividing the total number of cases by the population")
        st.dataframe(top_cases_df, use_container_width=True, hide_index=True)
        
    with col4:
        st.subheader("Highest Mortality Rate", help = "The mortality rate is calculated by divinding the number of deaths by the population" )
        st.dataframe(top_deaths_df, use_container_width=True, hide_index=True)

with tab2:
    st.title("SIRD Model", help="Select a country in the sidebar to see detailed SIRD-Model graphs for the selected country")
    
    # Sidebar selection
    st.sidebar.header("SIRD Model")
    available_countries = creating_available_countries()
    selected_country = st.sidebar.selectbox("Select a Country", available_countries)

    st.header(f"SIRD Model for COVID-19 in {selected_country}")

    col1, col2 = st.columns([1, 1]) 

    #Call the function to generate the plot
    with col1:
        fig = plot_sird_model(selected_country)
        if fig:
            st.pyplot(fig)
        else:
            st.warning(f"No data available for {selected_country}.")

    with col2:
        fig_smoothed_sird = plot_smooth_sird(selected_country)
        if fig_smoothed_sird:
            st.pyplot(fig_smoothed_sird)
        else:
            st.warning(f"No data available for {selected_country}.")

    st.divider()

    # Create two columns for side-by-side layout
    col3, col4 = st.columns([1, 1]) 


    # Estimate parameters and fetch data
    r0_data = estimate_parameters(selected_country)

    # Display R0 Trajectory in the first column
    with col3:
        st.subheader(rf"Reproduction Rate ($R_0$) Over Time")
        fig_r0 = plot_R0_trajectory(r0_data, selected_country)
        if fig_r0:
            st.pyplot(fig_r0)
        else:
            st.error(rf"No ($R_0$) data available for {selected_country}.")

    # Display Death Rate Trajectory in the second column
    with col4:
        st.subheader(rf"Death Rate ($\mu$) Over Time")
        fig_death = plot_death_rate(r0_data, selected_country)
        if fig_death:
            st.pyplot(fig_death)
        else:
            st.error(rf"No death rate ($\mu$) data available for {selected_country}.")

    col5, col6 = st.columns(2)
    
    # Display Alpha Trajectory in the third column
    with col5:
        st.subheader(rf"Alpha ($\alpha$) Over Time")
        fig_alpha = plot_alpha(r0_data, selected_country)
        if fig_alpha:
            st.pyplot(fig_alpha)
        else:
            st.error(rf"No alpha ($\alpha$) data available for {selected_country}.")
    
    # Display Beta Trajectory in the fourth column
    with col6:
        st.subheader(rf"Beta ($\beta$) Over Time")
        fig_beta = plot_beta(r0_data, selected_country)
        if fig_beta:
            st.pyplot(fig_beta)
        else:
            st.error(rf"No ($\beta$) data available for {selected_country}.")

with tab3:
    st.title("USA Statistics", help="Hover over the maps to see detailed data")
    st.plotly_chart(plot_usa_choropleth(connection), use_container_width=True) 

    col1, col2 = st.columns([1, 1])
                            
    with col1:
        st.plotly_chart(plot_confirmed_cases_map(connection))


    with col2:
        st.plotly_chart(plot_deaths_map(connection), help="Hover over the map to see the US counties with the most Covid-19 deaths")

    
    st.divider()

    col3, col4 = st.columns([1, 1])

    with col3:
        st.subheader("US Counties with Most Cases", help = "US counties with the most Covid-19 cases")
        top_x_confirmed = get_top_x_data(connection, 'Confirmed')[["Admin2" , "Total"]]
        top_x_confirmed = top_x_confirmed.rename(columns={"Admin2": "County", "Total": "Confirmed Cases"})
        st.dataframe(top_x_confirmed, use_container_width=True, hide_index=True)

    with col4:
        st.subheader("US Counties with Most Deaths", help = "US counties with the most Covid-19 deaths")
        top_x_deaths = get_top_x_data(connection, 'Deaths')[["Admin2", "Total"]]
        top_x_deaths = top_x_deaths.rename(columns={"Admin2": "County", "Total": "Deaths"})
        st.dataframe(top_x_deaths, use_container_width=True, hide_index=True)

