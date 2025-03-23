import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# Connect to the database/CSV
db_path = "covid_database.db"
connection = sqlite3.connect(db_path)
df = pd.read_csv("cleaned_complete.csv")

 # Create a lit of all unique countries
def creating_available_countries():
    return sorted(df["Country.Region"].unique())

 # Get population from db
def get_population_from_db(country):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    country_mapping = {
        "US": "USA",
        "Holy See": "Vatican City", 
        "United Kingdom": "UK"
    }
    
    mapped_country = country_mapping.get(country, country)
    
    query = "SELECT Population FROM worldometer_data WHERE `Country.Region` = ?"
    cursor.execute(query, (mapped_country,))
    result = cursor.fetchone()
    
    connection.close()
    
    if result:
        return result[0]
    else:
        return None

# Estimate parameters for the SIRD Model
def estimate_parameters(country):
    actual_population = get_population_from_db(country)
    if actual_population is None:
        return pd.DataFrame()  # Return empty DataFrame if population data is not found
    
    # Filter data for the selected country
    country_df = df[df["Country.Region"] == country].copy()
    if country_df.empty:
        return pd.DataFrame()
    
    # Convert Date column to datetime
    country_df["Date"] = pd.to_datetime(country_df["Date"])
    country_df.sort_values("Date", inplace=True)
    
    # Use actual population from a country
    N = actual_population
    country_df["S"] = N - (country_df["Active"] + country_df["Recovered"] + country_df["Deaths"])
    
    # Compute daily changes
    country_df["DeltaD"] = country_df["Deaths"].diff().fillna(0)
    country_df["DeltaR"] = country_df["Recovered"].diff().fillna(0)
    country_df["DeltaI"] = country_df["Active"].diff().fillna(0)
    
    # Estimate mortality rate (mu)
    country_df["mu"] = (country_df["DeltaD"] / country_df["Active"]).clip(lower=0).fillna(0)
    
    # Assume gamma (recovery rate) as 1/4.5 days
    country_df["gamma"] = 1 / 4.5
    
    # Estimate beta (transmission rate)
    country_df["beta"] = ((country_df["DeltaI"] + country_df["gamma"] * country_df["Active"] + country_df["mu"] * country_df["Active"]) / ((country_df["S"] * country_df["Active"]) / N)).clip(lower=0).fillna(0)
    
    # Estimate alpha (loss of immunity rate) as alpha = DeltaR / Recovered
    country_df["alpha"] = (country_df["DeltaR"] / country_df["Recovered"]).clip(lower=0).fillna(0)
    
    # Compute R0
    country_df["R0"] = (country_df["beta"] / country_df["gamma"]).clip(lower=0).fillna(0)
    
    return country_df[["Date", "alpha", "beta", "gamma", "mu", "R0"]]

# Smoothen the SIRD parameter functions
def get_smooth_function(country):
    # Getting the dataframe and selecting the amount of iterations
    df_parameters = estimate_parameters(country)
    n = 10

    # Creating new columns for the smoothed parameters
    df_parameters['smoothed_alpha'] = df_parameters['alpha'].rolling(window=3, center=True).mean()
    df_parameters['smoothed_beta'] = df_parameters['beta'].rolling(window=3, center=True).mean()
    df_parameters['smoothed_mu'] = df_parameters['mu'].rolling(window=3, center=True).mean()
    df_parameters['smoothed_R0'] = df_parameters['R0'].rolling(window=3, center=True).mean()

    # Iterating n times for a smoother function
    for i in range(0,n):
        df_parameters['smoothed_mu'] = df_parameters['smoothed_mu'].rolling(window=3, center=True).mean()
        df_parameters['smoothed_alpha'] = df_parameters['smoothed_alpha'].rolling(window=3, center=True).mean()
        df_parameters['smoothed_beta'] = df_parameters['smoothed_beta'].rolling(window=3, center=True).mean()
        df_parameters['smoothed_R0'] = df_parameters['smoothed_R0'].rolling(window=3, center=True).mean()
    
    return df_parameters

# Generate an R0 trajectory plot for the selected country.
def plot_R0_trajectory(df, country):
    if df.empty:
        return None 
    
    # Get dataframe of the smoothed function
    df_smoothed = get_smooth_function(country)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["R0"], linestyle="-", color="lightblue", label=f"Reproduction rate ($R_0$)")
    ax.plot(df_smoothed["Date"], df_smoothed["smoothed_R0"], linestyle="-", color="red", label="Smoothed reproduction rate ($R_0$)")
    ax.set_xlabel("Date")
    ax.set_ylabel(rf"Reproduction Rate ($R_0$)")
    ax.set_title(rf"Reproduction rate ($R_0$) Over Time for {country}")
    ax.legend()
    plt.xticks(rotation=45)

    return fig  

# Generate a death rate trajectory plot for the selected country.
def plot_death_rate(df, country):
    if df.empty:
        return None  

    # Get dataframe of the smoothed function
    df_smoothed = get_smooth_function(country)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["mu"], linestyle="-", color="lightblue", label=f"Death Rate ($\mu$)")
    ax.plot(df_smoothed["Date"], df_smoothed["smoothed_mu"], linestyle="-", color="red", label=f"Smoothed Death Rate ($\mu$)")
    ax.set_xlabel("Date")
    ax.set_ylabel(rf"Death Rate ($\mu$)")
    ax.set_title(rf"Death Rate ($\mu$) Over Time for {country}")
    ax.legend()
    plt.xticks(rotation=45)
    
    return fig

# Plot alpha for a slected country
def plot_alpha(df, country):
    if df.empty:
        return None  

    # Get dataframe of the smoothed function
    df_smoothed = get_smooth_function(country)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["alpha"], linestyle="-", color="lightblue", label=rf"Alpha ($\alpha$)")
    ax.plot(df_smoothed["Date"], df_smoothed["smoothed_alpha"], linestyle="-", color="red", label=rf"Smoothed Alpha ($\alpha$)")
    ax.set_xlabel("Date")
    ax.set_ylabel(rf"Alpha ($\alpha$)")
    ax.set_title(rf"Alpha ($\alpha$) Over Time for {country}")
    ax.legend()
    plt.xticks(rotation=45)
    
    return fig

# Plot beta for a selected country
def plot_beta(df, country):
    if df.empty:
        return None  

    # Get dataframe of the smoothed function
    df_smoothed = get_smooth_function(country)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["beta"], linestyle="-", color="lightblue", label=rf"Beta ($\beta$)")
    ax.plot(df_smoothed["Date"], df_smoothed["smoothed_beta"], linestyle="-", color="red", label=rf"Smoothed Beta ($\beta$)")
    ax.set_xlabel("Date")
    ax.set_ylabel(rf"Beta ($\beta$)")
    ax.set_title(rf"Beta ($\beta$) Over Time for {country}")
    ax.legend()
    plt.xticks(rotation=45)
    
    return fig

# Plot the SIRD Model for a selected country
def plot_sird_model(selected_country):
    country_df = get_smooth_function_SIRD(selected_country)

    # Compute daily new cases, deaths, and recovered
    country_df["New_Cases"] = country_df["Confirmed"].diff().clip(lower=0).fillna(0)
    country_df["New_Deaths"] = country_df["Deaths"].diff().clip(lower=0).fillna(0)
    country_df["New_Recovered"] = country_df["Recovered"].diff().clip(lower=0).fillna(0)

    # Plot data
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(country_df["Date"], country_df["New_Cases"], label="Infected", color="blue")
    ax.plot(country_df["Date"], country_df["New_Deaths"], label="Deaths", color="red")
    ax.plot(country_df["Date"], country_df["New_Recovered"], label="Recovered", color="green")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cases")
    ax.set_title(f"COVID-19 Cases in {selected_country}")
    ax.legend()
    plt.xticks(rotation=45)

    return fig

# Get the smooth function fot a selected country
def get_smooth_function_SIRD(selected_country):
    # Load data and selecting amount of iterations
    df = pd.read_csv("cleaned_complete.csv", parse_dates=["Date"])
    n = 10

    # Filter data for selected country
    country_df = df[df["Country.Region"] == selected_country].copy()

    if country_df.empty:
        return None  # Return None if no data is available for the selected country

    # Sort by date to ensure correct calculations
    country_df.sort_values("Date", inplace=True)

    # Compute daily new cases, deaths, and recovered
    country_df["New_Cases"] = country_df["Confirmed"].diff().clip(lower=0).fillna(0)
    country_df["New_Deaths"] = country_df["Deaths"].diff().clip(lower=0).fillna(0)
    country_df["New_Recovered"] = country_df["Recovered"].diff().clip(lower=0).fillna(0)

    # Creating new column for the smoothed new cases, deaths and recovered
    country_df['smoothed_cases'] = country_df['New_Cases'].rolling(window=3, center=True).mean()
    country_df['smoothed_deaths'] = country_df['New_Deaths'].rolling(window=3, center=True).mean()
    country_df['smoothed_recovered'] = country_df['New_Recovered'].rolling(window=3, center=True).mean()

    for i in range(0,n):
        country_df['smoothed_cases'] = country_df['smoothed_cases'].rolling(window=3, center=True).mean()
        country_df['smoothed_deaths'] = country_df['smoothed_deaths'].rolling(window=3, center=True).mean()
        country_df['smoothed_recovered'] = country_df['smoothed_recovered'].rolling(window=3, center=True).mean()
    
    return country_df

# Plot the smoothened SIRD model
def plot_smooth_sird(selected_country):
    # Loading data 
    country_df = get_smooth_function_SIRD(selected_country)

    # Plot data
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(country_df["Date"], country_df["smoothed_cases"], label="Infected", color="blue")
    ax.plot(country_df["Date"], country_df["smoothed_deaths"], label="Deaths", color="red")
    ax.plot(country_df["Date"], country_df["smoothed_recovered"], label="Recovered", color="green")
    
    ax.set_xlabel("Date")
    ax.set_ylabel("Cases")
    ax.set_title(f"Smoothed COVID-19 Cases in {selected_country}")
    ax.legend()
    plt.xticks(rotation=45)

    return fig

