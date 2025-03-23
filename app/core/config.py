import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required")

# Model settings
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")

# Environment settings
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# API settings
API_V1_PREFIX = "/api/v1"

# CORS settings
CORS_ORIGINS: List[str] = []
if ENVIRONMENT == "development":
    CORS_ORIGINS = ["*"]
else:
    # In production, specify exact origins
    cors_origins_str = os.getenv("CORS_ORIGINS", "")
    if cors_origins_str:
        CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",")]
    else:
        CORS_ORIGINS = ["https://your-domain.com"]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO") 