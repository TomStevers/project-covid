import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Connect to the database
db_path = "covid_database.db"
connection = sqlite3.connect(db_path)

def get_latest_date(connection):
    """
    Retrieves the most recent date available in the dataset.
    """
    query = "SELECT MAX(Date) FROM usa_county_wise"
    latest_date = pd.read_sql(query, connection).iloc[0, 0]
    return latest_date

def get_top_x_data(connection, column_name):
    """
    Fetches the top 5 counties in the U.S. based on the given column (Confirmed or Deaths),
    only for the most recent available date.
    """
    latest_date = get_latest_date(connection)  # **Retrieve latest available date**
    
    query = f"""
        SELECT 
            Province_State, 
            Admin2, 
            Lat, 
            Long_, 
            SUM({column_name}) AS Total
        FROM usa_county_wise
        WHERE Country_Region = 'US' 
        AND Date = '{latest_date}'  -- **Filter for the latest date**
        GROUP BY Province_State, Admin2
        ORDER BY Total DESC
        LIMIT 10
    """
    df = pd.read_sql(query, connection)
    df['Category'] = 'Confirmed' if column_name == 'Confirmed' else 'Deaths'
    return df

def create_map(dataframe, category):
    """
    Creates a scatter geo map for the given data.
    """
    color_map = {'Confirmed': 'red', 'Deaths': 'blue'}
    fig = px.scatter_geo(dataframe,
                         lat='Lat', 
                         lon='Long_',
                         color='Category',
                         color_discrete_map=color_map,
                         hover_name='Admin2',
                         hover_data=['Province_State', 'Total'],
                         title=f"Top 10 U.S. Counties with Most {category} Cases",
                         scope="usa")
    return fig

def plot_confirmed_cases_map(connection):
    top_x_confirmed = get_top_x_data(connection, 'Confirmed')
    return create_map(top_x_confirmed, 'Confirmed')

def plot_deaths_map(connection):
    top_x_deaths = get_top_x_data(connection, 'Deaths')
    return create_map(top_x_deaths, 'Deaths')

# Mapping of full state names to abbreviations
STATE_ABBREVIATIONS = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

def plot_usa_choropleth(connection):
    """
    Creates a choropleth map of confirmed COVID-19 cases by state, using the most recent date.
    """
    latest_date = get_latest_date(connection)  # **Retrieve latest available date**
    
    query = f"""
        SELECT 
            Province_State AS State, 
            SUM(Confirmed) AS "Total Confirmed"
        FROM usa_county_wise
        WHERE Country_Region = 'US' 
        AND Date = '{latest_date}'  -- **Filter for the latest date**
        AND Province_State NOT IN ('American Samoa', 'Guam', 'Northern Mariana Islands', 'Puerto Rico', 'Virgin Islands')
        GROUP BY Province_State
    """
    df = pd.read_sql(query, connection)

    # Convert full state names to abbreviations
    df["State"] = df["State"].map(STATE_ABBREVIATIONS)

    fig = px.choropleth(df, 
                        locations="State", 
                        locationmode="USA-states",
                        color="Total Confirmed",
                        color_continuous_scale="Turbo",
                        title="Total Confirmed COVID-19 Cases by State",
                        scope="usa")
    return fig
