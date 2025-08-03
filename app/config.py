import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

MASTER_KEY = os.environ["MASTER_KEY"]
MONGO_URI  = os.getenv("MONGO_URI", "mongodb://localhost:27017")