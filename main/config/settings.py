SPARK_CONFIG = {
    "app_name": "BridebookScraper",
    "driver_memory": "4g",
    "executor_memory": "4g",
    "max_result_size": "2g"
}

SELENIUM_CONFIG = {
    "timeout": 10,
    "implicit_wait": 5
}

DATA_PATHS = {
    "input_csv": "cleaned_venues.csv",
    "output_csv": "venue_reviews_spark.csv"
}