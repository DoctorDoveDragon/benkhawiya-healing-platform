from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import sqlite3
import os
import uvicorn
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Benkhawiya Healing Platform",
    description="Complete ancestral spiritual healing system through the Four Lands",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
@contextmanager
def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect('benkhawiya.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# CULTURAL FOUNDATION: THE FOUR LANDS
FOUR_LANDS = {
    "white_land": {
        "name": "White Land of Origins",
        "element": "Spirit",
        "direction": "Center",
        "teaching": "Pure Consciousness & Ancestral Memory",
        "animal": "White Buffalo",
        "color": "White",
        "symbol": "🦬",
        "practice": "Ancestral recall and spiritual purification",
        "blessing": "May the White Land awaken your ancestral memory and pure consciousness",
        "cosmic_aspect": "NTU - Essence/Being/Consciousness"
    },
    "black_land": {
        "name": "Black Land of Potential", 
        "element": "Void",
        "direction": "Within",
        "teaching": "Unmanifest Potential & Quantum Possibility",
        "animal": "Black Panther",
        "color": "Black",
        "symbol": "🐆",
        "practice": "Deep meditation on unmanifest potential",
        "blessing": "May the Black Land reveal the infinite possibilities within the void",
        "cosmic_aspect": "SEWU - Foundation/Memory/Structure"
    },
    "red_land": {
        "name": "Red Land of Manifestation",
        "element": "Blood/Fire",
        "direction": "Manifest", 
        "teaching": "Life Force & Physical Creation",
        "animal": "Red Hawk",
        "color": "Red",
        "symbol": "🦅",
        "practice": "Energy work and life force activation",
        "blessing": "May the Red Land ignite your creative life force and power to manifest",
        "cosmic_aspect": "PELU - Truth/Measurement/Time"
    },
    "green_land": {
        "name": "Green Land of Growth",
        "element": "Earth/Life",
        "direction": "Expand",
        "teaching": "Regeneration & Collective Life", 
        "animal": "Green Serpent",
        "color": "Green",
        "symbol": "🐍",
        "practice": "Healing and regenerative practices",
        "blessing": "May the Green Land connect you to all living beings and cycles of regeneration",
        "cosmic_aspect": "RUWA - Flow/Energy/Relationship"
    }
}

HEALING_PRACTICES = [
    {
        "id": "white_ancestral_recall",
        "name": "White Land: Ancestral Memory Activation", 
        "land": "white_land",
        "description": "Connect with the White Land's pure consciousness through ancestral recall",
        "duration": 20,
        "difficulty": "advanced",
        "steps": [
            "Sit facing North in pure white light",
            "Chant: 'Ntu dumo, sewu karibu' (Essence speaks, foundation approaches)",
            "Visualize white buffalo emerging from mist", 
            "Receive ancestral memories as white light",
            "Ask: 'Ntu se sewu wapi?' (Where is the foundation of being?)"
        ],
        "cultural_context": "The White Land holds the pure consciousness that precedes all manifestation - the Ntu of all being"
    },
    {
        "id": "black_quantum_void", 
        "name": "Black Land: Quantum Potential Meditation",
        "land": "black_land",
        "description": "Enter the Black Land's void to access unmanifest quantum possibilities", 
        "duration": 25,
        "difficulty": "advanced",
        "steps": [
            "Enter complete darkness or blindfold",
            "Chant: 'Sewu wapi, ntu tayari' (Foundation where, essence ready)",
            "Feel the black panther's silent movement",
            "Become the void of infinite possibility", 
            "Question: 'Pelu ya wewe ni nini?' (What is your truth?)"
        ],
        "cultural_context": "The Black Land is the Sewu - the foundational quantum field where all possibilities exist before manifestation"
    }
]

# Routes
@app.get("/")
async def root():
    return {"message": "Benkhawiya Healing Platform", "version": "3.0.0", "status": "active", "database": "sqlite"}

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "benkhawiya-healing-platform", 
        "database": "sqlite_operational",
        "cosmology": "Four Lands Tradition",
        "lands": list(FOUR_LANDS.keys())
    }

# Cultural endpoints
@app.get("/four-lands")
async def get_four_lands():
    return FOUR_LANDS

@app.get("/practices/daily")
async def daily_practice():
    day_of_year = datetime.now().timetuple().tm_yday
    practice_data = HEALING_PRACTICES[day_of_year % len(HEALING_PRACTICES)]
    land_info = FOUR_LANDS[practice_data["land"]]
    
    return {
        "practice": practice_data,
        "land_info": land_info,
        "day_of_year": day_of_year,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cultural_blessing": land_info["blessing"]
    }

@app.get("/practices/all")
async def all_practices():
    return HEALING_PRACTICES

# Simple user endpoints without authentication
@app.post("/auth/register")
async def register(email: str, spiritual_name: str = None):
    try:
        with get_db_connection() as conn:
            # Simple registration without password for now
            cursor = conn.execute(
                "INSERT INTO users (email, spiritual_name, password_hash) VALUES (?, ?, ?)",
                (email, spiritual_name, "simple_auth")
            )
            user_id = cursor.lastrowid
            
            # Initialize land progress
            for land_id in FOUR_LANDS.keys():
                conn.execute(
                    "INSERT INTO user_land_progress (user_id, land_id) VALUES (?, ?)",
                    (user_id, land_id)
                )
            
            conn.commit()
            
            return {
                "message": "Welcome to the Benkhawiya journey",
                "user_id": user_id,
                "spiritual_name": spiritual_name,
                "status": "registered"
            }
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.get("/user/progress/{user_id}")
async def get_user_progress(user_id: int):
    try:
        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT spiritual_name, current_land, journey_streak FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            land_progress = conn.execute(
                """SELECT land_id, practices_completed, total_duration 
                   FROM user_land_progress WHERE user_id = ?""",
                (user_id,)
            ).fetchall()
            
            return {
                "spiritual_name": user["spiritual_name"],
                "current_land": FOUR_LANDS[user["current_land"]],
                "journey_streak": user["journey_streak"],
                "land_progress": [
                    {
                        "land": FOUR_LANDS[progress["land_id"]],
                        "practices_completed": progress["practices_completed"],
                        "total_duration": progress["total_duration"]
                    }
                    for progress in land_progress
                ]
            }
            
    except Exception as e:
        logger.error(f"Progress retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve progress")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
