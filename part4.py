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
df_cleaned.to_csv("cleaned_file.csv", index=False)

# Look for missing values
missing_values = df.isnull().sum()

# Print 
print(f"Total Rows Before : {before_count}")
print(f"Total Rows After: {after_count}")
print(f"Duplicates removed: {before_count - after_count}")
print("Missing values per column:\n", missing_values)





