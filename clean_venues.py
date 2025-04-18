import json
import pandas as pd
import re

# Load the JSON file
with open("hitched_venues_enriched.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# 1. Fix broken URLs (if any)
df['url'] = df['url'].str.replace(
    "https://www.hitched.co.ukhttps://www.hitched.co.uk", 
    "https://www.hitched.co.uk", 
    regex=False
)

# 2. Clean location
df['location'] = df['location'].str.replace("·", "", regex=False).str.replace(r"\s+", " ", regex=True).str.strip()

# 3. Extract capacity min and max
df[["min_capacity", "max_capacity"]] = df["capacity"].str.extract(r"(\d+)\s*(?:to)?\s*(\d+)?")
df["min_capacity"] = pd.to_numeric(df["min_capacity"], errors="coerce")
df["max_capacity"] = pd.to_numeric(df["max_capacity"], errors="coerce")

# 4. Extract price as float
df["price_numeric"] = df["price_text"].str.extract(r"([\d,\.]+)")[0].str.replace(",", "").astype(float)

# 5. Reorder columns to bring price_type next to price_numeric
cols = list(df.columns)
if "price_type" in cols and "price_numeric" in cols:
    cols.remove("price_type")
    insert_at = cols.index("price_numeric") + 1
    cols.insert(insert_at, "price_type")
    df = df[cols]

# 6 Reorder columns
column_order = [
    "name", "location", "rating", "no_of_reviews",
    "price_text", "price_type", "price_numeric",
    "capacity", "min_capacity", "max_capacity", "url"
]
df = df.reindex(columns=column_order)

# 7 Replace all missing/NaN values with "N/A"
df = df.fillna("N/A")

# 8 Save to CSV
df.to_csv("cleaned_venues.csv", index=False)
print("✅ Cleaned data saved to cleaned_venues.csv with N/A filled in")