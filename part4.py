import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Load the CSV file
df = pd.read_csv("complete.csv")

# Remove duplicates
before_count = df.shape[0]
df_cleaned = df.drop_duplicates(keep='first')
after_count = df_cleaned.shape[0]

# Replace missing values with 0
df_cleaned = df_cleaned.fillna(0)

# Save the cleaned DataFrame back to CSV
df_cleaned.to_csv("cleaned_complete.csv", index=False)

# Look for missing values (after replacement)
missing_values = df_cleaned.isnull().sum()

# Print
print(f"Total Rows Before : {before_count}")
print(f"Total Rows After: {after_count}")
print(f"Duplicates removed: {before_count - after_count}")
print("Missing values per column (after replacement):\n", missing_values)





