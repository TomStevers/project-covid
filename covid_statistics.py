import sqlite3
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

db_path = "covid_database.db"

def get_db_connection():
    """Create and return a new database connection."""
    return sqlite3.connect(db_path, check_same_thread=False)

def plot_continent_map(continent):
    connection = get_db_connection()
    
    if continent == "All":
        query = """
            SELECT "Country.Region" AS "Country", TotalCases AS "Total Cases", Population
            FROM worldometer_data
            WHERE Continent IS NOT NULL
        """
    else:
        query = """
            SELECT "Country.Region" AS "Country", TotalCases AS "Total Cases", Population
            FROM worldometer_data
            WHERE continent = ?
        """
    
    df_continent_map = pd.read_sql(query, connection, params=(continent,) if continent != "All" else None)
    connection.close()  # Close connection after fetching data
    
    df_continent_map["Log Total Cases"] = np.log1p(df_continent_map["Total Cases"])
    
    fig = px.choropleth(
        df_continent_map, 
        locations="Country", 
        locationmode="country names", 
        color="Log Total Cases", 
        color_continuous_scale="Blues",
        hover_name="Country",  # Show country name on hover
        hover_data={"Total Cases": True, "Log Total Cases": False, "Country": False}  # Show actual cases, hide log values
    )

    # Custom hover template: removes extra space by formatting the text
    fig.update_traces(
        hovertemplate="<b>%{location}</b>: %{customdata[0]:,} Cases",  # Removes extra line break
        customdata=df_continent_map[["Total Cases"]].values  # Pass actual case count
    )


    # Update color bar labels
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Log(Total Cases)",  # Label the color bar correctly
            tickmode="array",
            tickvals=np.log1p([1, 10, 100, 1000, 10000, 100000, 1000000]),  # Log-scaled tick marks
            ticktext=["1", "10", "100", "1K", "10K", "100K", "1M"]  # Readable labels
        )
    )


    return fig

def compare_death_rates():
    connection = get_db_connection()
    query = """
        SELECT Continent, SUM(TotalDeaths) AS Deaths, SUM(Population) AS Population
        FROM worldometer_data
        WHERE Continent IS NOT NULL
        GROUP BY Continent
    """
    df = pd.read_sql(query, connection)
    connection.close()
    
    df["DeathRate"] = df["Deaths"] / df["Population"]
    
    fig = px.pie(
        df, 
        names="Continent", 
        values="DeathRate", 
        title="Death Rates Across Continents", 
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Reds
    )
    
    return fig

def top_countries_by_cases():
    connection = get_db_connection()
    query = """
        SELECT "Country.Region" AS Countries, TotalCases AS "Total Cases"
        FROM worldometer_data
        WHERE Population IS NOT NULL
        ORDER BY TotalCases DESC
        LIMIT 5
    """
    df_cases = pd.read_sql(query, connection)
    connection.close()
    
    return df_cases

def top_countries_by_deathrate():
    connection = get_db_connection()
    query = """
        SELECT "Country.Region" AS Countries, (TotalDeaths * 1.0 / Population) AS "Death Rate"
        FROM worldometer_data
        WHERE Population IS NOT NULL
        ORDER BY "Death Rate" DESC
        LIMIT 5
    """
    df_deaths = pd.read_sql(query, connection)
    connection.close()

    return df_deaths

def get_totals(start_date, end_date):
    connection = get_db_connection()
    
    query = f"""
        SELECT Date, Active, Deaths, Recovered, Confirmed
        FROM day_wise 
        WHERE Date BETWEEN '{start_date}' AND '{end_date}' 
        ORDER BY Date DESC LIMIT 1;
    """
    
    latest_row = pd.read_sql(query, connection)
    connection.close()
    
    if not latest_row.empty:
        total_active = latest_row['Active'].values[0]
        total_deaths = latest_row['Deaths'].values[0]
        total_recovered = latest_row['Recovered'].values[0]
        total_confirmed = latest_row['Confirmed'].values[0]
    else:
        total_active = total_deaths = total_recovered = total_confirmed = 0
    
    return total_active, total_deaths, total_recovered, total_confirmed

def plot_totals(start_date, end_date):
    connection = get_db_connection()
    
    query = f"""
        SELECT Date, Active, Deaths, Recovered 
        FROM day_wise 
        WHERE Date BETWEEN '{start_date}' AND '{end_date}' 
        ORDER BY Date;
    """
    
    filtered_data = pd.read_sql(query, connection)
    connection.close()
    
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
