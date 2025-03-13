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

st.pyplot(compare_death_rates())
plt.show
   

selected_country = st.selectbox("Select a Country", available_countries)
df_selected_country = available_countries == selected_country
plot_R0_trajectory(df_selected_country)