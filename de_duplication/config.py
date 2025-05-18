import os
from dotenv import load_dotenv
load_dotenv() # loads config from .env file

# # Feature toggles
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# Kafka
BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS")
TOPIC_SCRAPED_ITEMS = os.getenv("TOPIC_SCRAPED_ITEMS")
TOPIC_NEW_ITEMS = os.getenv("TOPIC_NEW_ITEMS")

# Redis
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
TTL = os.getenv("TTL", 86400)


