import os
from dotenv import load_dotenv
load_dotenv() # loads config from .env file

# Scraper settings
MAX_QUEUE_SIZE = int(os.environ.get("MAX_QUEUE_SIZE", 10))
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", 20))
NUM_CONTEXTS = int(os.environ.get("NUM_CONTEXTS", 4))
TRACE_ENABLED = os.getenv("TRACE_ENABLED", False)
TRACE_PATH = os.getenv("TRACE_PATH", False)

# Feature toggles
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Search params
JOB_SOURCE = os.getenv("JOB_SOURCE", "file").lower()
JOB_FILE_PATH = os.getenv("JOB_FILE_PATH", "job_params/search_params_subset.txt").lower()
VIEWPORT_WIDTH = int(os.environ.get("VIEWPORT_WIDTH", 1920))
VIEWPORT_HEIGHT = int(os.environ.get("VIEWPORT_HEIGHT", 1080))


