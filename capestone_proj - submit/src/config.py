"""
Configuration loader for the AI Stock Market Research Assistant.
Supports reading from local .env or Databricks workspace secrets.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load local .env file if available
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

LAKEBASE_URL = os.environ.get(
    "LAKEBASE_URL",
    "postgresql://student:npg_2UsJqVOcW8kw@ep-wandering-flower-d8v8axnp.database.us-east-2.cloud.databricks.com/databricks_postgres?sslmode=require"
)

MASSIVE_API_BASE_URL = os.environ.get("MASSIVE_API_BASE_URL", "https://api.massive.com")
MASSIVE_SECRET_SCOPE = os.environ.get("MASSIVE_SECRET_SCOPE", "massive")
MASSIVE_SECRET_KEY = os.environ.get("MASSIVE_SECRET_KEY", "api-key")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
