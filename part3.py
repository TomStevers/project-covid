import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Connect to the database
db_path = "covid_database.db"
connection = sqlite3.connect(db_path)

# Load country-wise and worldometer data
query = """
    SELECT c."Country.Region", c.Confirmed, c.Deaths, c.Recovered, c.Active, w.Population
    FROM country_wise c
    JOIN worldometer_data w ON c."Country.Region" = w."Country.Region"
"""
df = pd.read_sql(query, connection)

# Normalize by population
df["Active_Rate"] = df["Active"] / df["Population"]
df["Death_Rate"] = df["Deaths"] / df["Population"]
df["Recovery_Rate"] = df["Recovered"] / df["Population"]

# Plot cases over time for a given country
country = "United States"
daywise_query = f"""
    SELECT Date, Active, Deaths, Recovered FROM day_wise
"""
df_daywise = pd.read_sql(daywise_query, connection)
df_daywise["Date"] = pd.to_datetime(df_daywise["Date"])

plt.figure(figsize=(12, 6))
plt.plot(df_daywise["Date"], df_daywise["Active"], label="Active Cases")
plt.plot(df_daywise["Date"], df_daywise["Deaths"], label="Deaths")
plt.plot(df_daywise["Date"], df_daywise["Recovered"], label="Recovered")
plt.legend()
plt.xlabel("Date")
plt.ylabel("Count")
plt.title(f"COVID-19 Trends Over Time")
plt.xticks(rotation=45)
plt.show()


# Generate a color-coded map of Europe
european_map_query = """
    SELECT "Country.Region", ActiveCases, Population
    FROM worldometer_data
    WHERE continent = 'Europe'
"""
df_european_map = pd.read_sql(european_map_query, connection)
df_european_map["Cases_Per_Person"] = df_european_map["ActiveCases"] / df_european_map["Population"]

fig = px.choropleth(df_european_map, locations="Country.Region", locationmode="country names", 
                    color="Cases_Per_Person", scope="europe",
                    title="European Countries with Active Cases",
                    color_continuous_scale="Turbo")
fig.show()


# Query to get top 5 counties with the most confirmed cases
query_confirmed = """
    SELECT 
        Province_State, 
        Admin2, 
        SUM(Confirmed) AS Total_Confirmed
    FROM usa_county_wise
    WHERE Country_Region = 'US' 
    GROUP BY Province_State, Admin2
    ORDER BY Total_Confirmed DESC
    LIMIT 5
"""
top_5_confirmed = pd.read_sql(query_confirmed, connection)

# Query to get top 5 counties with the most deaths
query_deaths = """
    SELECT 
        Province_State, 
        Admin2, 
        SUM(Deaths) AS Total_Deaths
    FROM usa_county_wise
    WHERE Country_Region = 'US' 
    GROUP BY Province_State, Admin2
    ORDER BY Total_Deaths DESC
    LIMIT 5
"""
top_5_deaths = pd.read_sql(query_deaths, connection)

# Combine both lists into one DataFrame (for the purpose of coloring)
# Mark confirmed cases counties as 'Confirmed' and death counties as 'Deaths'
top_5_confirmed['Category'] = 'Confirmed'
top_5_deaths['Category'] = 'Deaths'

# Merge both DataFrames
top_5_combined = pd.concat([top_5_confirmed[['Province_State', 'Admin2', 'Total_Confirmed', 'Category']],
                            top_5_deaths[['Province_State', 'Admin2', 'Total_Deaths', 'Category']]])

# If there are counties that appear in both lists, combine their information
top_5_combined = top_5_combined.groupby(['Province_State', 'Admin2', 'Category']).agg({
    'Total_Confirmed': 'sum',
    'Total_Deaths': 'sum'
}).reset_index()

# Create a new color column based on the category
top_5_combined['Color'] = top_5_combined['Category'].map({'Confirmed': 'red', 'Deaths': 'blue'})

# Query to fetch lat/long for counties (if available in the database)
query_confirmed = """
    SELECT 
        Province_State, 
        Admin2, 
        SUM(Confirmed) AS Total_Confirmed
    FROM usa_county_wise
    WHERE Country_Region = 'US' 
    GROUP BY Province_State, Admin2
    ORDER BY Total_Confirmed DESC
    LIMIT 5
"""
top_5_confirmed = pd.read_sql(query_confirmed, connection)

# Query to get top 5 counties with the most deaths
query_deaths = """
    SELECT 
        Province_State, 
        Admin2, 
        SUM(Deaths) AS Total_Deaths
    FROM usa_county_wise
    WHERE Country_Region = 'US' 
    GROUP BY Province_State, Admin2
    ORDER BY Total_Deaths DESC
    LIMIT 5
"""
top_5_deaths = pd.read_sql(query_deaths, connection)

# Create new columns for confirmed and deaths categories
top_5_confirmed['Category'] = 'Confirmed'
top_5_deaths['Category'] = 'Deaths'

# Merge both DataFrames
top_5_combined = pd.concat([top_5_confirmed[['Province_State', 'Admin2', 'Total_Confirmed', 'Category']],
                            top_5_deaths[['Province_State', 'Admin2', 'Total_Deaths', 'Category']]])

# Identify counties that are in both top 5 confirmed and deaths lists
both_counties = set(top_5_confirmed['Admin2']).intersection(set(top_5_deaths['Admin2']))

# Update the 'Category' for counties in both lists
top_5_combined['Category'] = top_5_combined.apply(lambda row: 'Both' if row['Admin2'] in both_counties else row['Category'], axis=1)

# Create a new column for color coding
top_5_combined['Color'] = top_5_combined['Category'].map({'Confirmed': 'red', 'Deaths': 'blue', 'Both': 'purple'})

# Query to fetch lat/long for counties (if available in the database)
map_query = """
    SELECT 
        Province_State, 
        Admin2, 
        Lat, 
        Long_
    FROM usa_county_wise
    WHERE Country_Region = 'US' AND (Admin2 IN ('{}'))
""".format("', '".join(top_5_combined['Admin2']))  # Get the top counties' lat/long

# Get the corresponding lat/long for the top counties
df_map = pd.read_sql(map_query, connection)

# Merge the top 5 counties info (Confirmed/Deaths) with lat/long info
df_map = df_map.merge(top_5_combined, on=['Province_State', 'Admin2'])

# Generate the choropleth map with distinct colors
fig = px.scatter_geo(df_map,
                     lat='Lat', 
                     lon='Long_',
                     color='Category',
                     color_discrete_map={'Confirmed': 'red', 'Deaths': 'blue', 'Both': 'purple'},
                     hover_name='Admin2',
                     hover_data=['Province_State', 'Total_Confirmed', 'Total_Deaths'],
                     title="Top 5 U.S. Counties with Most Confirmed Cases (Red), Most Deaths (Blue), and Both (Purple)",
                     scope="usa")

# Show the map
fig.show()




