import json
import csv
from pathlib import Path
from utils.file_utils import save_to_json, log_message

# Setup paths
input_path = Path("data/raw/venue_all_details.json")
output_dir = Path("data/processed")
log_file = Path("logs/cleaner_log.txt")

venue_csv_path = output_dir / "venue_cleaned.csv"
supplier_csv_path = output_dir / "venue_suppliers.csv"
deal_csv_path = output_dir / "venue_deals.csv"

output_dir.mkdir(parents=True, exist_ok=True)

# Load JSON data
with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Setup headers
venue_headers = [
    "venue_no", "venue_name", "region", "location", "rating", "no_of_reviews",
    "price_text", "price_type", "price_numeric",
    "min_capacity", "max_capacity",
    "url", "description",
    "venue_type_tags", "dining_options", "ceremony_options",
    "entertainment_options", "social_links"
]

supplier_headers = [
    "venue_no", "venue_name", "supplier_name", "supplier_url",
    "supplier_image", "supplier_rating", "supplier_category"
]

deal_headers = [
    "venue_no", "venue_name", "deal_type", "deal_title", "expires_on"
]

try:
    # Open all three files
    with open(venue_csv_path, "w", newline="", encoding="utf-8") as venue_f, \
         open(supplier_csv_path, "w", newline="", encoding="utf-8") as supplier_f, \
         open(deal_csv_path, "w", newline="", encoding="utf-8") as deal_f:

        venue_writer = csv.DictWriter(venue_f, fieldnames=venue_headers)
        supplier_writer = csv.DictWriter(supplier_f, fieldnames=supplier_headers)
        deal_writer = csv.DictWriter(deal_f, fieldnames=deal_headers)

        venue_writer.writeheader()
        supplier_writer.writeheader()
        deal_writer.writeheader()

        for venue in data:
            # Save venue main info
            venue_writer.writerow({
                "venue_no": venue.get("venue_no"),
                "venue_name": venue.get("name"),
                "region": venue.get("region"),
                "location": venue.get("location"),
                "rating": venue.get("rating"),
                "no_of_reviews": venue.get("no_of_reviews"),
                "price_text": venue.get("price_text"),
                "price_type": venue.get("price_type"),
                "price_numeric": venue.get("price_numeric"),
                "min_capacity": venue.get("min_capacity"),
                "max_capacity": venue.get("max_capacity"),
                "url": venue.get("url"),
                "description": venue.get("description"),
                "venue_type_tags": ", ".join(venue.get("venue_type_tags", [])),
                "dining_options": ", ".join(venue.get("dining_options", [])),
                "ceremony_options": ", ".join(venue.get("ceremony_options", [])),
                "entertainment_options": ", ".join(venue.get("entertainment_options", [])),
                "social_links": ", ".join(venue.get("social_links", [])),
            })

            # Save suppliers
            for supplier in venue.get("preferred_suppliers", []):
                supplier_writer.writerow({
                    "venue_no": venue.get("venue_no"),
                    "venue_name": venue.get("name"),
                    "supplier_name": supplier.get("vendor_name"),
                    "supplier_url": supplier.get("vendor_url"),
                    "supplier_image": supplier.get("vendor_image"),
                    "supplier_rating": supplier.get("rating_text"),
                    "supplier_category": supplier.get("category"),
                })

            # Save deals
            for deal in venue.get("deals", []):
                deal_writer.writerow({
                    "venue_no": venue.get("venue_no"),
                    "venue_name": venue.get("name"),
                    "deal_type": deal.get("type"),
                    "deal_title": deal.get("title"),
                    "expires_on": deal.get("expires_on"),
                })

    log_message(log_file, f"✅ Successfully saved venues ({len(data)}), suppliers, and deals.")
    print(f"✅ Done! Cleaned venues, suppliers, and deals into separate CSV files!")

except Exception as e:
    log_message(log_file, f"❌ Cleaning failed: {str(e)}")
    print("❌ Error during cleaning:", e)