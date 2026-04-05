import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "leads.db"
EXPORT_DIR = BASE_DIR / "dashboard" / "public" / "data"

# SerpAPI (https://serpapi.com - 100 free searches/month)
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# Google PageSpeed Insights (free)
PAGESPEED_API_KEY = os.getenv("PAGESPEED_API_KEY", "")

# Email - SMTP
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "amanchahar175@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "amanchahar175@gmail.com")
FROM_NAME = os.getenv("FROM_NAME", "Aman Kumar")

# Resend API (alternative)
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")

# Your info
YOUR_NAME = os.getenv("YOUR_NAME", "Aman Kumar")
YOUR_EMAIL = os.getenv("YOUR_EMAIL", "amanchahar175@gmail.com")
PORTFOLIO_BASE_URL = os.getenv("PORTFOLIO_BASE_URL", "https://your-app.vercel.app")

# Agent settings
SCRAPE_DELAY = float(os.getenv("SCRAPE_DELAY", "2.0"))
MAX_RESULTS_PER_QUERY = int(os.getenv("MAX_RESULTS_PER_QUERY", "20"))
