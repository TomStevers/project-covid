import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import part3

st.set_page_config(
    page_title="Covid Project",
    layout="wide",
    initial_sidebar_state="expanded")

with st.sidebar:
    st.title('Sidebar')

st.pyplot(part3.compare_death_rates())
plt.show
    


    # Hallo test