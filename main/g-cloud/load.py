from google.cloud import storage
import os
from pathlib import Path
import logging
from datetime import datetime
import sys

# Add the project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from main.utils.file_utils import setup_directories

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def upload_to_gcs(bucket_name, source_path, destination_blob_name):
    """Uploads a file to Google Cloud Storage bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        blob.upload_from_filename(source_path)
        logger.info(f"File {source_path} uploaded to {destination_blob_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to upload {source_path}: {str(e)}")
        return False

def main():
    # GCS bucket name
    BUCKET_NAME = "bkt-wedding-venues-uk"
    
    # Use Directories class to get the correct processed data path
    dirs = setup_directories()
    base_dir = dirs.processed_dir
    
    # List of files to upload
    files_to_upload = [
        "cleaned_venues.csv",
        "cleaned_regions.csv",
        "venue_reviews.csv",
        "cleaned_venues_details.csv",
        "cleaned_venues_suppliers.csv",
        "cleaned_venues_deals.csv"
    ]
    
    # Create timestamped folder in GCS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    successful_uploads = 0
    failed_uploads = 0
    
    for file_name in files_to_upload:
        source_file = base_dir / file_name
        if not source_file.exists():
            logger.warning(f"Source file not found: {source_file}")
            continue
            
        # Create GCS path with timestamp
        destination_blob = f"processed_data/{timestamp}/{file_name}"
        
        if upload_to_gcs(BUCKET_NAME, str(source_file), destination_blob):
            successful_uploads += 1
        else:
            failed_uploads += 1
    
    logger.info(f"Upload complete: {successful_uploads} successful, {failed_uploads} failed")

if __name__ == "__main__":
    main()