import pandas as pd
import sqlite3 
import numpy as np

def getDataFrame(table):
    connection = sqlite3.connect('covid_database.db')
    cursor = connection.cursor()
    
    # Construct the SQL query
    query = f"SELECT * FROM {table}"  

    cursor.execute(query)  # Execute query
    rows = cursor.fetchall()  # Fetch data

    # Get column names dynamically
    column_names = [desc[0] for desc in cursor.description]

    # Create DataFrame with correct column names
    df = pd.DataFrame(rows, columns=column_names)

    return df, column_names  # Return both DataFrame and column names

# List of tables
tables = ["country_wise", "day_wise", "usa_county_wise", "worldometer_data"]

# Loop through each table and print column names + data
for table in tables:
    print(100 * "-")
    print(f"Data from {table}")
    df, columns = getDataFrame(table)
    print("Columns:", columns)
    print(100 * "-")
    print(df)


