import sqlite3
import pandas as pd
import numpy as np
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

    return df_continent_map

# df = plot_continent_map("All").sort_values(by = ['Population'], ascending = False)
# df['Cases Fraction'] = df['Total Cases']/df['Population']
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#     print(df)

def update_database():
    # List of all countries that need to be updated
    countries = ['UK', 'Spain', 'Netherlands', 'Sweden']
    
    # List of new active cases, based on the active cases of a similar country
    cases_fractions = [86204.0, 86204.0, 64503.0, 661.0]

    # Establish a persistent database connection
    db_path = "covid_database.db"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Updating active cases and total recovered for the required countries

    # Active cases is calculated by taking the fraction 
    # of active cases and total population of a similar country
    # and multiplying this fraction by the total population
    # of the required country

    # Total recovered is calculated by taking the total recovered
    # and divding this by the total cases of a similar country
    # then multiplying this fraction by the total cases of
    # the required country

    for country in countries:
        if country == 'UK':
            update_query = f"""
            UPDATE worldometer_data
            SET ActiveCases = 86204.0, TotalRecovered = 129880.0
            WHERE "Country.Region" = 'UK'
            """
        elif country == 'Spain':
            update_query = f"""
            UPDATE worldometer_data
            SET ActiveCases = 59341.0, TotalRecovered = 149436.0
            WHERE "Country.Region" = 'Spain'
            """
        elif country == 'Netherlands':
            update_query = f"""
            UPDATE worldometer_data
            SET ActiveCases = 64503.0, TotalRecovered = 14143.0
            WHERE "Country.Region" = 'Netherlands'
            """
        else:
            update_query = f"""
            UPDATE worldometer_data
            SET ActiveCases = 661.0, TotalRecovered = 76677.0
            WHERE "Country.Region" = 'Sweden'
            """

        cursor.execute(update_query)
        connection.commit()

    connection.close()



