"""Configuration management."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Reddit
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "pain-point-discovery:v1.0")

# LLM
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "data" / "painpoints.db"))

# Scraping config
DEFAULT_SUBREDDITS = [
    "SaaS", "startups", "Entrepreneur", "smallbusiness",
    "webdev", "programming", "productivity", "selfhosted",
    "sideproject", "indiehackers", "digitalnomad", "nocode",
]
SUBREDDITS = os.getenv("SUBREDDITS", ",".join(DEFAULT_SUBREDDITS)).split(",")
SCRAPE_LIMIT = int(os.getenv("SCRAPE_LIMIT", "50"))

# Pain point keywords
PAIN_KEYWORDS = [
    "i wish", "frustrated", "annoying", "why isn't there",
    "looking for", "need a tool", "hate when", "pain point",
    "struggle with", "wish there was", "anyone know of",
    "alternative to", "tired of", "can't find", "doesn't exist",
    "would pay for", "shut up and take my money", "feature request",
    "deal breaker", "broken", "sucks", "terrible", "worst part",
    "is there a", "recommend a", "help me find", "what do you use for",
    "so annoying", "drives me crazy", "waste of time", "looking for something",
]

CATEGORIES = [
    "Productivity", "Developer Tools", "Business", "Communication",
    "Finance", "Health", "Education", "Marketing", "Design",
    "Data & Analytics", "Automation", "Other"
]
