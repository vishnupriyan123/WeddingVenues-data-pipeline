import json
import pandas as pd
import time
import re
import os
from datetime import datetime

# Make sure data/processed and logs folders exist
os.makedirs("../data/processed", exist_ok=True)
os.makedirs("../logs", exist_ok=True)

# Load the JSON file
with open("../data/raw/hitched_venues.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Fix broken URLs
df['url'] = df['url'].str.replace(
    "https://www.hitched.co.ukhttps://www.hitched.co.uk", 
    "https://www.hitched.co.uk", 
    regex=False
)

# Extracting Location
df['location'] = df['location'].str.replace("·", "", regex=False).str.replace(r"\s+", " ", regex=True).str.strip()

# Extracting capacity min and max
df[["min_capacity", "max_capacity"]] = df["capacity"].str.extract(r"(\d+)\s*(?:to)?\s*(\d+)?")
df["min_capacity"] = pd.to_numeric(df["min_capacity"], errors="coerce")
df["max_capacity"] = pd.to_numeric(df["max_capacity"], errors="coerce")

# Extracting price as float
df["price_numeric"] = df["price_text"].str.extract(r"([\d,\.]+)")[0].str.replace(",", "").astype(float)

# Reordering columns
cols = list(df.columns)
if "price_type" in cols and "price_numeric" in cols:
    cols.remove("price_type")
    insert_at = cols.index("price_numeric") + 1
    cols.insert(insert_at, "price_type")
    df = df[cols]

column_order = [
    "name", "location", "rating", "no_of_reviews",
    "price_text", "price_type", "price_numeric",
    "capacity", "min_capacity", "max_capacity", "url"
]
df = df.reindex(columns=column_order)

# imputation
df = df.fillna("N/A")

# Save latest version (for use in dashboard tools)
df.to_csv("../data/processed/cleaned_venues.csv", index=False)
print("Cleaned data saved to cleaned_venues.csv")

# Save timestamped version (for logging/auditing)
timestamp = datetime.now().strftime("%Y%m%d")
df.to_csv(f"../data/processed/cleaned_venues_{timestamp}.csv", index=False)
print(f"Snapshot saved to cleaned_venues_{timestamp}.csv")

with open("../logs/cleaner_log.txt", "a") as log:
    log.write(f"Cleaned {len(df)} rows on {time.ctime()}\n")