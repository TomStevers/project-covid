import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from part3 import *

st.set_page_config(
    page_title="Covid Project",
    layout="wide",
    initial_sidebar_state="expanded")

with st.sidebar:
    st.title('Sidebar')


# Load available countries from CSV
available_countries = creating_available_countries()

# Streamlit UI
st.title("COVID-19 $R_0$ Dashboard")

# Dropdown for country selection
selected_country = st.sidebar.selectbox("Select a Country", available_countries)

# Compute R0 for the selected country
r0_data = estimate_parameters(selected_country)

# Plot and display the R0 trajectory
fig = plot_R0_trajectory(r0_data, selected_country)

if fig:
    st.pyplot(fig)
else:
    st.error(f"No R₀ data available for {selected_country}.")