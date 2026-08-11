
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")
WAZE_API_KEY = os.getenv("WAZE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "wejhatna"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD")