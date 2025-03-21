import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt

def update_database():
    # List of all countries that need to be updated
    countries = ['UK', 'Spain', 'Netherlands', 'Sweden', 'China', 'CAR']
    
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
        # France was used for the calculations of the active cases and total recovered for the UK
        if country == 'UK':
            update_query = f"""
            UPDATE worldometer_data
            SET ActiveCases = 86204.0, TotalRecovered = 129880.0
            WHERE "Country.Region" = 'UK'
            """
        # France was used for the calculations of the active cases and total recovered for Spain
        elif country == 'Spain':
            update_query = f"""
            UPDATE worldometer_data
            SET ActiveCases = 59341.0, TotalRecovered = 149436.0
            WHERE "Country.Region" = 'Spain'
            """
        # Belgium was used for the calculations of the active cases and total recovered for the Netherlands
        elif country == 'Netherlands':
            update_query = f"""
            UPDATE worldometer_data
            SET ActiveCases = 64503.0, TotalRecovered = 14143.0
            WHERE "Country.Region" = 'Netherlands'
            """
        # Norway was used for the calculations of the active cases and total recovered for Sweden
        elif country == 'Sweden':
            update_query = f"""
            UPDATE worldometer_data
            SET ActiveCases = 661.0, TotalRecovered = 76677.0
            WHERE "Country.Region" = 'Sweden'
            """
        # India was used for the calculations of the total cases, active cases, total deaths and total recovered for China
        # The data for Population was the approximate population of China in 2020
        elif country == 'China' :
            # Checking if China already exists so if the function is runs twice there won't be a duplicate row 
            cursor.execute("SELECT COUNT(*) FROM worldometer_data WHERE \"Country.Region\" = 'China'")
            exists = cursor.fetchone()[0]

            if exists == 0:
                update_query = f""" 
                INSERT INTO worldometer_data ('Country.Region', Continent, Population, TotalCases, TotalDeaths, TotalRecovered, ActiveCases, 'WHO.Region')
                VALUES ("China", "Asia", 1411000000.0, 2068891.0, 42532.0, 1406954.0, 619405.0, "WesternPacific")
                """
        # Changing the name of CAR to Central African Republic
        else :
            update_query = f"""
            UPDATE worldometer_data
            SET "Country.Region" = 'Central African Republic'
            WHERE "Country.Region" = 'CAR'
            """

        cursor.execute(update_query)
        connection.commit()

    connection.close()

update_database()


