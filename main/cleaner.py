import json
import pandas as pd
import time
import re
import os
import logging
from datetime import datetime

# Make sure necessary folders exist
os.makedirs("data/processed", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Set up logging
logging.basicConfig(
    filename="logs/cleaner_log.txt",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

try:
    # Load the JSON file
    with open("data/raw/all_venues.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Fix broken URLs
    df['url'] = df['url'].str.replace(
        "https://www.hitched.co.ukhttps://www.hitched.co.uk", 
        "https://www.hitched.co.uk", 
        regex=False
    )

    # Clean location
    df['location'] = df['location'].str.replace("·", "", regex=False)\
        .str.replace(r"\s+", " ", regex=True).str.strip()

    # Extract min and max capacity
    df[["min_capacity", "max_capacity"]] = df["capacity"].str.extract(r"(\d+)\s*(?:to)?\s*(\d+)?")
    df["min_capacity"] = pd.to_numeric(df["min_capacity"], errors="coerce")
    df["max_capacity"] = pd.to_numeric(df["max_capacity"], errors="coerce")

    # Parse price as float
    df["price_numeric"] = df["price_text"].str.extract(r"([\d,\.]+)")[0].str.replace(",", "").astype(float)

    # Reorder columns
    cols = list(df.columns)
    if "price_type" in cols and "price_numeric" in cols:
        cols.remove("price_type")
        insert_at = cols.index("price_numeric") + 1
        cols.insert(insert_at, "price_type")
        df = df[cols]

    column_order = [
        "name", "region", "location", "rating", "no_of_reviews",
        "price_text", "price_type", "price_numeric",
        "capacity", "min_capacity", "max_capacity", "url"
    ]
    df = df.reindex(columns=column_order)

    # Imputation
    df = df.fillna("N/A")

    # Save latest version
    latest_path = "data/processed/cleaned_venues.csv"
    df.to_csv(latest_path, index=False)
    logging.info("Cleaned data saved to %s", latest_path)

    # Save timestamped version
    timestamp = datetime.now().strftime("%Y%m%d")
    timestamped_path = f"data/processed/cleaned_venues_{timestamp}.csv"
    df.to_csv(timestamped_path, index=False)
    logging.info("Snapshot saved to %s", timestamped_path)

    # Final log
    logging.info("Cleaned %d rows successfully", len(df))
    print("Cleaned succesfully!")

except Exception as e:
    logging.error("Cleaner failed with error: %s", str(e))
    print("Cleaning failed,check logs for more info.")
    