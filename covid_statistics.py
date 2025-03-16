import sqlite3
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# Establish a persistent database connection
db_path = "covid_database.db"
connection = sqlite3.connect(db_path)

def plot_continent_map(continent):
    if continent == "All":
        query = """
            SELECT "Country.Region", ActiveCases, Population
            FROM worldometer_data
            WHERE Continent IS NOT NULL
        """
        df_continent_map = pd.read_sql(query, connection)
    else:
        query = """
            SELECT "Country.Region", ActiveCases, Population
            FROM worldometer_data
            WHERE continent = ?
        """
        df_continent_map = pd.read_sql(query, connection, params=(continent,))
    
    df_continent_map["Total Cases"] = df_continent_map["ActiveCases"] 
    # / df_continent_map["Population"]
    
    fig = px.choropleth(
        df_continent_map, 
        locations="Country.Region", 
        locationmode="country names", 
        color="Total Cases", 
        # title=f"{continent if continent != 'All' else 'All Continents'} Countries with Active Cases", 
        color_continuous_scale="Turbo"
    )

    return fig

def compare_death_rates():
    query = """
        SELECT Continent, SUM(TotalDeaths) AS Deaths, SUM(Population) AS Population
        FROM worldometer_data
        WHERE Continent IS NOT NULL
        GROUP BY Continent
    """
    df = pd.read_sql(query, connection)
    
    df["DeathRate"] = df["Deaths"] / df["Population"]
    
    fig = px.pie(
        df, 
        names="Continent", 
        values="DeathRate", 
        title="Death Rates Across Continents", 
        hole=0.4,  # Creates a donut chart
        color_discrete_sequence=px.colors.sequential.Reds
    )
    
    return fig

def top_countries_by_cases():
    query = """
        SELECT "Country.Region" AS Countries, TotalCases AS "Total Cases"
        FROM worldometer_data
        WHERE Population IS NOT NULL
        ORDER BY TotalCases DESC
        LIMIT 5
    """
    df_cases = pd.read_sql(query, connection)
    
    return df_cases

def top_countries_by_deathrate():
    query = """
        SELECT "Country.Region" AS Countries, (TotalDeaths * 1.0 / Population) AS "Death Rate"
        FROM worldometer_data
        WHERE Population IS NOT NULL
        ORDER BY "Death Rate" DESC
        LIMIT 5
    """
    df_deaths = pd.read_sql(query, connection)

    return df_deaths

def get_totals(start_date, end_date):

    query = f"""
        SELECT Date, Active, Deaths, Recovered, Confirmed
        FROM day_wise 
        WHERE Date BETWEEN '{start_date}' AND '{end_date}' 
        ORDER BY Date DESC LIMIT 1;
    """
    latest_row = pd.read_sql(query, connection)
    
    if not latest_row.empty:
        total_active = latest_row['Active'].values[0]
        total_deaths = latest_row['Deaths'].values[0]
        total_recovered = latest_row['Recovered'].values[0]
        total_confirmed = latest_row['Confirmed'].values[0]
    else:
        total_active = total_deaths = total_recovered = total_confirmed = 0
    
    return total_active, total_deaths, total_recovered, total_confirmed

def plot_totals(start_date, end_date):

    query = f"""
        SELECT Date, Active, Deaths, Recovered 
        FROM day_wise 
        WHERE Date BETWEEN '{start_date}' AND '{end_date}' 
        ORDER BY Date;
    """
    filtered_data = pd.read_sql(query, connection)
    
    plt.figure(figsize=(12, 4))
    plt.plot(filtered_data['Date'], filtered_data['Active'], label='Active Cases', color='blue')
    plt.plot(filtered_data['Date'], filtered_data['Deaths'], label='Deaths', color='red')
    plt.plot(filtered_data['Date'], filtered_data['Recovered'], label='Recovered', color='green')
    plt.xlabel('Date')
    plt.ylabel('Count')
    plt.title('COVID-19 Trends')
    plt.xticks(rotation=45)
    plt.xticks([filtered_data['Date'].iloc[0], filtered_data['Date'].iloc[-1]])
    plt.legend()
    return plt