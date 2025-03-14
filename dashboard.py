import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from part3 import *
from sird_model import *

import streamlit as st

st.set_page_config(
    page_title="Covid Project",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title('Sidebar')

# Load available countries from CSV
available_countries = creating_available_countries()

# Streamlit UI
st.title("COVID-19 Dashboard")

# Dropdown for country selection
selected_country = st.sidebar.selectbox("Select a Country", available_countries)

# Compute R0 and death rate for the selected country
r0_data = estimate_parameters(selected_country)

# Create two columns for side-by-side plots
col1, col2 = st.columns([1, 1])

# Plot and display the R0 trajectory
with col1:
    # st.subheader(f"R_0 Over Time")
    fig_r0 = plot_R0_trajectory(r0_data, selected_country)
    if fig_r0:
        st.pyplot(fig_r0)
    else:
        st.error(f"No R₀ data available for {selected_country}.")

# Plot and display the death rate trajectory
with col2:
    # st.subheader(f"Death Rate Over Time")
    fig_death = plot_death_rate(r0_data, selected_country)
    if fig_death:
        st.pyplot(fig_death)
    else:
        st.error(f"No death rate data available for {selected_country}.")
