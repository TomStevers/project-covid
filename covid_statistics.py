import sqlite3
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

db_path = "covid_database.db"
csv_path = "cleaned_complete.csv" 
df = pd.read_csv(csv_path, parse_dates=["Date"])

# Create and return a new database connection
def get_db_connection():
    return sqlite3.connect(db_path, check_same_thread=False)

# Create continent map
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
    df_continent_map["Log Total Cases"] = np.log1p(df_continent_map["Total Cases"])

    connection.close()  
    
    fig = px.choropleth(
        df_continent_map, 
        locations="Country", 
        locationmode="country names", 
        color="Log Total Cases", 
        color_continuous_scale="Blues",
        hover_name="Country",  
        hover_data={"Total Cases": True, "Log Total Cases": False, "Country": False}  
    )

    scope_mapping = {
        "All": "world",
        "Europe": "europe",
        "Asia": "asia",
        "Africa": "africa",
        "North America": "north america",
        "South America": "south america",
        "Australia/Oceania": None  
    }

    # Custom hover template
    fig.update_traces(
        hovertemplate="<b>%{location}</b>: %{customdata[0]:,} Cases", 
        customdata=df_continent_map[["Total Cases"]].values  
    )

    # Update color bar labels
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Log(Total Cases)",  
            tickmode="array",
            tickvals=np.log1p([1, 10, 100, 1000, 10000, 100000, 1000000]),  # Log-scaled tick marks
            ticktext=["1", "10", "100", "1K", "10K", "100K", "1M"]  
        ),
        geo=dict(
            scope=scope_mapping.get(continent, "world"),
            showcoastlines=True,
            showland=False
        )
    )

    # Custom handling for Australia/Oceania
    if continent == "Australia/Oceania":
        fig.update_layout(
            geo=dict(
                projection_type="orthographic",
                center={"lat": -25, "lon": 140},
                lataxis_range=[-50, 10],
                lonaxis_range=[110, 180],
            )
        )

    return fig

# Compare deathrate per continent
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
    df["DeathRate"] *= 100  

    # Create bar chart 
    fig = px.bar(
        df, 
        x="Continent", 
        y="DeathRate", 
        title="COVID-19 Death Rates Across Continents", 
        labels={"DeathRate": "Death Rate (%)", "Continent": "Continent"},
        text=df["DeathRate"].round(2),  
        color="DeathRate",  
        color_continuous_scale=px.colors.sequential.Blues
    )

    # Improve layout
    fig.update_traces(textposition="outside")  
    fig.update_layout(yaxis=dict(title="Death Rate (%)"), xaxis=dict(title="Continent"))

    return fig

# Find the countries with the most cases
def top_countries_by_cases():
    connection = get_db_connection()
    query = """
        SELECT "Country.Region" AS Countries, ((TotalCases * 1.0 / Population) * 100) AS "Total Cases"
        FROM worldometer_data
        WHERE Population IS NOT NULL
        ORDER BY "Total Cases" DESC
        LIMIT 10
    """
    df_cases = pd.read_sql(query, connection) 
    connection.close()

    df_cases["Total Cases"] = df_cases["Total Cases"].map(lambda x: f"{x:.2f}%")
    
    return df_cases


# Find the countries with the highest deathrate
def top_countries_by_deathrate():
    connection = get_db_connection()
    query = """
        SELECT "Country.Region" AS Countries, ("Deaths.1M.pop" / 10000) AS "Death Rate"
        FROM worldometer_data
        WHERE Population IS NOT NULL
        ORDER BY "Death Rate" DESC
        LIMIT 10
    """
    df_deaths = pd.read_sql(query, connection)
    connection.close()

    df_deaths["Death Rate"] = df_deaths["Death Rate"].map(lambda x: f"{x:.2f}%")

    return df_deaths

# Get the total values for selected date
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

# Plot the totals for a selected date
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

# Creates an animated world map showing when each country first reported COVID-19.
def plot_covid_spread_animation():
    # Keep necessary columns
    df_filtered = df[["Country.Region", "Date", "Confirmed"]].copy()

    # Convert Confirmed cases to a binary indicator (1 if cases > 0, else 0)
    df_filtered["Had COVID"] = df_filtered["Confirmed"] > 0

    # Sort by date and keep only the first date when a country had a confirmed case
    df_first_case = df_filtered[df_filtered["Had COVID"]].groupby("Country.Region", as_index=False)["Date"].min()

    # Format the date as a string 
    df_first_case["First Case Date"] = df_first_case["Date"].dt.strftime('%Y-%m-%d')

    # Create a column to use for animation
    all_dates = df_filtered["Date"].dt.strftime('%Y-%m-%d').unique()
    all_dates = [date for date in all_dates if date <= "2020-05-20"] # Stops at 20th of May because every country has had a Covid cases at that point

    df_expanded = pd.DataFrame()
    for date in all_dates:
        temp = df_first_case[df_first_case["Date"].dt.strftime('%Y-%m-%d') <= date].copy()
        temp["Animation Date"] = date
        temp["Had COVID"] = 1 
        df_expanded = pd.concat([df_expanded, temp])

    # Ensure "Had COVID" is actually present in df_expanded
    df_expanded = df_expanded[["Country.Region", "Animation Date", "Had COVID", "First Case Date"]]

    fig = px.choropleth(
        df_expanded,
        locations="Country.Region",
        locationmode="country names",
        color_continuous_scale=["White", "Blue"], 
        hover_name="Country.Region",
        hover_data={"Had COVID": False, "First Case Date": True,"Country.Region": False, "Animation Date": False},  # Show first case date on hover
        animation_frame="Animation Date",
        title="Spread of COVID-19 Over Time"
    )

    # Add country borders
    fig.update_geos(
        showcountries=True,
        countrycolor="black",  
    )

    fig.update_layout(coloraxis_showscale=False, showlegend=False)

    return fig
