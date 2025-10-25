import os
from typing import List

class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key-for-dev-32-chars-min")
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        
        # Validate critical settings
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")

settings = Settings()
