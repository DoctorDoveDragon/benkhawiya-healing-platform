from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import os
import uvicorn

app = FastAPI(
    title="Benkhawiya Healing Platform",
    description="Authentic Benkhawiya Ancestral Healing System - Preserving the true tradition",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTHENTIC BENKHAWIYA TRADITION
# This is the real spiritual system, not generic animal guides

BENKHAWIYA_COSMOLOGY = {
    "teachings": {
        "foundation": "Ubuntu philosophy - I am because we are",
        "ancestral_connection": "Direct lineage to ancestral wisdom",
        "healing_modalities": ["Energy work", "Ancestral recall", "Spiritual cleansing"],
        "sacred_elements": ["Earth", "Water", "Fire", "Air", "Spirit"]
    },
    "practices": {
        "ancestral_communication": "Connecting with lineage ancestors",
        "energy_balancing": "Restoring spiritual equilibrium", 
        "dream_interpretation": "Receiving guidance through dreams",
        "sacred_rituals": "Traditional ceremonial practices"
    }
}

# Authentic endpoints
@app.get("/")
async def root():
    return {
        "message": "Authentic Benkhawiya Healing Platform",
        "version": "1.0.0", 
        "status": "active",
        "tradition": "Benkhawiya Ancestral Healing",
        "authentic": True
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "benkhawiya-healing-platform",
        "authentic": True
    }

@app.get("/cosmology")
async def get_cosmology():
    return BENKHAWIYA_COSMOLOGY

@app.get("/authentic")
async def authentic_check():
    return {
        "authentic": True,
        "message": "This is the authentic Benkhawiya tradition",
        "warning": "Previous versions with animal guides were incorrect"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
