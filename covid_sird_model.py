import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Connect to the database/CSV
db_path = "covid_database.db"
connection = sqlite3.connect(db_path)
df = pd.read_csv("cleaned_complete.csv")

def creating_available_countries():
    # Create a lit of all unique countries
    return sorted(df["Country.Region"].unique())

def get_population_from_db(country):
    # Get population from db
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


def estimate_parameters(country):
    # Estimate parameters for the SIRD Model
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
    country_df["mu"] = (country_df["DeltaD"] / country_df["Active"]).fillna(0)
    
    # Assume gamma (recovery rate) as 1/4.5 days
    country_df["gamma"] = 1 / 4.5
    
    # Estimate beta (transmission rate)
    country_df["beta"] = ((country_df["DeltaI"] + country_df["gamma"] * country_df["Active"] + country_df["mu"] * country_df["Active"]) / ((country_df["S"] * country_df["Active"]) / N)).fillna(0)
    
    # Estimate alpha (loss of immunity rate) as alpha = DeltaR / Recovered
    country_df["alpha"] = (country_df["DeltaR"] / country_df["Recovered"]).fillna(0)
    
    # Compute R0
    country_df["R0"] = (country_df["beta"] / country_df["gamma"]).clip(lower=0).fillna(0)
    
    return country_df[["Date", "alpha", "beta", "gamma", "mu", "R0"]]

def plot_R0_trajectory(df, country):
  # Generate an R0 trajectory plot for the selected country.
    if df.empty:
        return None 
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["R0"], linestyle="-", color="blue", label=f"$R_0$ for {country}")
    ax.set_xlabel("Date")
    ax.set_ylabel("$R_0$")
    ax.set_title(f"$R_0$ Over Time for {country}")
    ax.legend()
    plt.xticks(rotation=45)

    return fig  

def plot_death_rate(df, country):
    # Generate a death rate trajectory plot for the selected country.
    if df.empty:
        return None  
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["mu"], linestyle="-", color="red", label=f"Death Rate for {country}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Death Rate (μ)")
    ax.set_title(f"Death Rate Over Time for {country}")
    ax.legend()
    plt.xticks(rotation=45)
    
    return fig

