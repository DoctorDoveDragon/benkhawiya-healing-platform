from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import os
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Benkhawiya Healing Platform",
    description="Production API for spiritual healing practices",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Healing practices
HEALING_PRACTICES = [
    "Morning meditation: 15 minutes of mindful breathing",
    "Evening reflection: Gratitude journaling", 
    "Body scan relaxation technique",
    "Loving-kindness meditation for self and others",
    "Energy cleansing visualization"
]

@app.get("/")
async def root():
    return {
        "message": "Benkhawiya Healing Platform API",
        "version": "2.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health():
    """Health check - always returns healthy"""
    return {
        "status": "healthy", 
        "timestamp": datetime.utcnow().isoformat(),
        "service": "benkhawiya-healing-platform"
    }

@app.get("/practices/daily")
async def daily_practice():
    """Get daily practice"""
    day_of_year = datetime.now().timetuple().tm_yday
    practice = HEALING_PRACTICES[day_of_year % len(HEALING_PRACTICES)]
    
    return {
        "practice": practice,
        "day_of_year": day_of_year,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
