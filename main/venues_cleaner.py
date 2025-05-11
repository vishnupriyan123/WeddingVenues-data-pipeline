import json
import pandas as pd
import re
import traceback
from datetime import datetime
from utils.file_utils import setup_directories, log_message

# Setup directories and paths
dirs = setup_directories()
raw_file = dirs.raw_dir / "all_venues.json"
processed_file = dirs.processed_dir / "cleaned_venues.csv"
timestamp = datetime.now().strftime("%Y%m%d")
backup_file = dirs.backup_dir / f"cleaned_venues_{timestamp}.csv"
log_file = dirs.log_dir / "cleaner_log.txt"

try:
    # Load raw JSON
    with open(raw_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df.insert(0, "venue_no", ["V" + str(i) for i in range(1, len(df) + 1)])

    # Fix broken URLs
    df["url"] = df["url"].str.replace(
        "https://www.hitched.co.ukhttps://www.hitched.co.uk",
        "https://www.hitched.co.uk",
        regex=False
    )

    # Clean location text
    df["location"] = df["location"].str.replace("·", "", regex=False)\
                                     .str.replace(r"\s+", " ", regex=True).str.strip()

    # Extract numeric capacity range
    df[["min_capacity", "max_capacity"]] = df["capacity"].str.extract(r"(\d+)\s*(?:to)?\s*(\d+)?")
    df["min_capacity"] = pd.to_numeric(df["min_capacity"], errors="coerce")
    df["max_capacity"] = pd.to_numeric(df["max_capacity"], errors="coerce")

    # Extract numeric price
    df["price_numeric"] = df["price_text"].str.extract(r"([\d,\.]+)")[0].str.replace(",", "").astype(float)

    # Adjust column order
    if "price_type" in df.columns and "price_numeric" in df.columns:
        cols = list(df.columns)
        cols.remove("price_type")
        insert_at = cols.index("price_numeric") + 1
        cols.insert(insert_at, "price_type")
        df = df[cols]

    # Final column order
    final_columns = [
        "venue_no", "name", "region", "location", "rating", "no_of_reviews",
        "price_text", "price_type", "price_numeric",
        "capacity", "min_capacity", "max_capacity", "url"
    ]
    df = df.reindex(columns=final_columns)

    # Impute missing values
    df = df.fillna("N/A")

    # Save final cleaned CSV
    df.to_csv(processed_file, index=False)
    df.to_csv(backup_file, index=False)

    log_message(log_file, f"✅ Cleaned and saved {len(df)} venues.")
    print(f"✅ Cleaner ran successfully! Cleaned rows: {len(df)}")

except Exception as e:
    error_msg = f"❌ Cleaner failed: {e}\n{traceback.format_exc()}"
    log_message(log_file, error_msg)
    print("❌ Cleaning failed. Check logs for details.")
