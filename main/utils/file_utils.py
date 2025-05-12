import os
import json
from datetime import datetime
from pathlib import Path

class Directories:
    def __init__(self, base_data_dir="data"):
        #self.data_dir = Path(base_data_dir)
        self.data_dir = Path(__file__).resolve().parent.parent / base_data_dir
        self.processed_dir = self.data_dir / "processed"
        self.raw_dir = self.data_dir / "raw"
        self.log_dir = Path("logs")
        self.backup_dir = self.data_dir / "backups"

        for folder in [self.processed_dir, self.raw_dir, self.log_dir, self.backup_dir]:
            folder.mkdir(parents=True, exist_ok=True)

def setup_directories(base_data_dir="data"):
    """
    Initializes and returns a Directories object.
    """
    return Directories(base_data_dir)

def save_to_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def log_message(log_path, message):
    """
    Append a log message to a file with timestamp.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")