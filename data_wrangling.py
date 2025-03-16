import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load the CSV file
file_path = "complete.csv"  # Update this with your file path
df = pd.read_csv(file_path)

## Remove duplicates before processing
before_count = df.shape[0]
df_cleaned = df.drop_duplicates(keep="first")
after_count = df_cleaned.shape[0]

# List of countries to merge provinces into a single entry
countries_to_merge = ["China", "Canada", "Australia"]

# Separate data: one for merging, one for keeping as is
df_merge = df_cleaned[df_cleaned["Country.Region"].isin(countries_to_merge)]
df_other = df_cleaned[~df_cleaned["Country.Region"].isin(countries_to_merge)]

# Group by Country and Date to merge provinces per date entry
df_merged = df_merge.groupby(["Country.Region", "Date"], as_index=False).agg({
    "Confirmed": "sum",
    "Deaths": "sum",
    "Recovered": "sum",
    "Active": "sum",
    "WHO.Region": "first"  # Keep first WHO region entry
})

# Set fixed Lat/Long for merged countries
central_coords = {
    "China": (35.8617, 104.1954),
    "Canada": (56.1304, -106.3468),
    "Australia": (-25.2744, 133.7751),
}

df_merged["Lat"] = df_merged["Country.Region"].map(lambda x: central_coords[x][0])
df_merged["Long"] = df_merged["Country.Region"].map(lambda x: central_coords[x][1])

# Combine the merged data with the rest of the dataset
df_final = pd.concat([df_other, df_merged], ignore_index=True)

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







