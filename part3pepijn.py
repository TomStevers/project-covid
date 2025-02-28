import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

def getDataFrame(table, columns):
    connection = sqlite3.connect('covid_database.db')
    cursor = connection.cursor()
    
    # Construct the correct SQL query
    columns_str = ", ".join([f'"{col}"' for col in columns])  # Escape column names
    query = f'SELECT {columns_str} FROM "{table}"'  # Securely format table name
    cursor.execute(query)  # Execute query
    rows = cursor.fetchall()  # Fetch data

    # Create DataFrame with correct column names
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    connection.close()  # Close connection to avoid memory leaks
    return df

def get_population(country):
    connection = sqlite3.connect('covid_database.db')
    cursor = connection.cursor()

    query = """SELECT Population FROM worldometer_data WHERE "Country.Region" = ? """

    cursor.execute(query, (country,))
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cursor.description])
    population = df['Population'][0]

    return population

def estimates_alpha_beta(country):
    df = getDataFrame("country_wise", ["Country.Region", "Active", "Deaths", "Recovered"])
    df_country = df.loc[df['Country.Region'] == 'US']
    N = get_population(country)

    print(df_country)


def main():
    df = getDataFrame("day_wise", ["Active", "Deaths", "Recovered"])

    return df

estimates_alpha_beta('USA')

