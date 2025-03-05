import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Function that puts out a dataframe for the given table and columns
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

# Function for obtaining the population of the USA
def get_population_usa():
    connection = sqlite3.connect('covid_database.db')
    cursor = connection.cursor()

    query = """SELECT Population FROM worldometer_data WHERE "Country.Region" = "USA" """

    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns = [x[0] for x in cursor.description])
    population = df['Population'][0]

    return population

# Function for estimating parameters
def estimate_parameters_usa():
    # Getting the correct data from the USA
    df = getDataFrame("country_wise", ["Country.Region", "Active", "Deaths", "Recovered", "New.cases", "New.deaths", "New.recovered"])
    df_country = df.loc[df['Country.Region'] == 'US']

    # Defining variables
    N = get_population_usa()
    I = df_country["Active"]
    D = df_country["Deaths"]
    R = df_country["Recovered"]
    S = N - I - D - R
    delta_I = df_country["New.cases"]
    delta_D = df_country["New.deaths"]
    delta_R = df_country["New.recovered"]

    # Estimating parameters
    gamma = 1/4.5
    mu = delta_D/I
    alpha = (gamma*I - delta_R)/R
    beta = (N*(delta_I + (mu + gamma)*I))/(S*I)

    return [alpha, beta, gamma, mu]
    



