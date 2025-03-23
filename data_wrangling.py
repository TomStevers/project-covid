import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load the CSV file
file_path = "cleaned_complete.csv"  
df = pd.read_csv(file_path)

# Remove duplicates 
before_count = df.shape[0]
df_cleaned = df.drop_duplicates(keep="first")
after_count = df_cleaned.shape[0]

# List of countries to merge provinces into a single entry
countries_to_merge = ["China", "Canada", "Australia", "Faroe Islands"]

# Separate data
df_merge = df_cleaned[df_cleaned["Country.Region"].isin(countries_to_merge)]
df_other = df_cleaned[~df_cleaned["Country.Region"].isin(countries_to_merge)]

# Group by Country and Date to merge provinces per date entry
df_merged = df_merge.groupby(["Country.Region", "Date"], as_index=False).agg({
    "Confirmed": "sum",
    "Deaths": "sum",
    "Recovered": "sum",
    "Active": "sum",
    "WHO.Region": "first"  
})

# Set fixed Lat/Long for merged countries
central_coords = {
    "China": (35.8617, 104.1954),
    "Canada": (56.1304, -106.3468),
    "Australia": (-25.2744, 133.7751),
    "Faroe Islands": (61.8926, -6.9118)
}

df_merged["Lat"] = df_merged["Country.Region"].map(lambda x: central_coords[x][0])
df_merged["Long"] = df_merged["Country.Region"].map(lambda x: central_coords[x][1])

# Define territories to merge
territory_mapping = {
    "UK Overseas Territories": ["Bermuda", "Gibraltar", "Falkland Islands (Malvinas)", "Montserrat", "Turks and Caicos Islands", "Cayman Islands", "British Virgin Islands", "Anguilla", "Isle of Man", "Channel Islands"],
    "French Overseas Territories": ["Guadeloupe", "Martinique", "Réunion", "Mayotte", "New Caledonia", "French Polynesia", "Saint Pierre and Miquelon", "Wallis and Futuna", "French Guiana", "Reunion", "Saint Barthelemy", "St Martin"],
    "Caribbean Netherlands": ["Aruba", "Sint Maarten", "Curacao"]
}

# Assign fixed lat/long for merged territories
territory_coords = {
    "UK Overseas Territories": (18.2208, -63.0686),
    "French Overseas Territories": (-21.1151, 55.5364),
    "Caribbean Netherlands": (12.1784, -68.2385)
}

# Separate data for territories
df_other = df_other[~df_other["Province.State"].isin(sum(territory_mapping.values(), []))]
df_merged_list = []

# Process each group of territories
for new_region, territories in territory_mapping.items():
    df_territories = df_cleaned[df_cleaned["Province.State"].isin(territories)]
    df_grouped = df_territories.groupby(["Date"], as_index=False).agg({
        "Confirmed": "sum",
        "Deaths": "sum",
        "Recovered": "sum",
        "Active": "sum",
        "WHO.Region": "first" 
    })
    df_grouped["Country.Region"] = new_region
    df_grouped["Province.State"] = 0
    df_grouped["Lat"] = territory_coords[new_region][0]
    df_grouped["Long"] = territory_coords[new_region][1]
    df_merged_list.append(df_grouped)

# Combine all data
df_final = pd.concat([df_other, df_merged] + df_merged_list, ignore_index=True)

# Sort first by Date, then by Country.Region alphabetically
df_final = df_final.sort_values(by=["Date", "Country.Region"]).reset_index(drop=True)

# Replace missing values with 0
df_final = df_final.fillna(0)

# Save the cleaned DataFrame to a new CSV file
df_final.to_csv("cleaned_complete.csv", index=False)

# Look for missing values
missing_values = df_final.isnull().sum()

# Print summary
print(f"Total Rows Before : {before_count}")
print(f"Total Rows After: {after_count}")
print(f"Duplicates removed: {before_count - after_count}")
print("Missing values per column:\n", missing_values)
