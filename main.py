from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict
import sqlite3
import os
import uvicorn
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
import asyncio
from pydantic import BaseModel
import json
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

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "benkhawiya-sacred-four-lands-ancestral-key-2024")
ALGORITHM = "HS256"

# Database connection
@contextmanager
def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect('/tmp/benkhawiya.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_tables():
    """Initialize database tables"""
    with get_db_connection() as conn:
        # Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                spiritual_name VARCHAR(255),
                password_hash VARCHAR(255) NOT NULL,
                current_land VARCHAR(50) DEFAULT 'white_land',
                journey_streak INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_practice_at TIMESTAMP
            )
        ''')
        
        # Practice completions
        conn.execute('''
            CREATE TABLE IF NOT EXISTS practice_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                practice_id VARCHAR(100) NOT NULL,
                notes TEXT,
                duration_minutes INTEGER,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User progress
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_land_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id),
                land_id VARCHAR(50) NOT NULL,
                practices_completed INTEGER DEFAULT 0,
                total_duration INTEGER DEFAULT 0,
                last_visited TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    logger.info("Database tables initialized")

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

# Pydantic Models
class UserCreate(BaseModel):
    email: str
    password: str
    spiritual_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class PracticeCompletion(BaseModel):
    practice_id: str
    notes: Optional[str] = None
    duration_minutes: int

# Authentication functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Application startup
@app.on_event("startup")
async def startup_event():
    init_tables()
    logger.info("Benkhawiya Healing Platform started successfully with SQLite database")

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

# Authentication endpoints
@app.post("/auth/register")
@limiter.limit("5/minute")
async def register(request: Request, user: UserCreate):
    try:
        with get_db_connection() as conn:
            # Check if user exists
            existing = conn.execute("SELECT id FROM users WHERE email = ?", (user.email,)).fetchone()
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Create user
            hashed_password = get_password_hash(user.password)
            cursor = conn.execute(
                "INSERT INTO users (email, spiritual_name, password_hash) VALUES (?, ?, ?)",
                (user.email, user.spiritual_name, hashed_password)
            )
            user_id = cursor.lastrowid
            
            # Initialize land progress
            for land_id in FOUR_LANDS.keys():
                conn.execute(
                    "INSERT INTO user_land_progress (user_id, land_id) VALUES (?, ?)",
                    (user_id, land_id)
                )
            
            conn.commit()
            
            # Create token
            token = create_access_token({"sub": user.email})
            
            return {
                "message": "Welcome to the Benkhawiya journey",
                "user_id": user_id,
                "spiritual_name": user.spiritual_name,
                "access_token": token,
                "token_type": "bearer"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, user: UserLogin):
    try:
        with get_db_connection() as conn:
            db_user = conn.execute(
                "SELECT id, email, spiritual_name, password_hash, current_land, journey_streak FROM users WHERE email = ?",
                (user.email,)
            ).fetchone()
            
            if not db_user or not verify_password(user.password, db_user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Update last login
            conn.execute(
                "UPDATE users SET last_practice_at = ? WHERE id = ?",
                (datetime.now(timezone.utc), db_user["id"])
            )
            conn.commit()
            
            token = create_access_token({"sub": db_user["email"]})
            
            return {
                "message": "Welcome back to your healing journey",
                "user_id": db_user["id"],
                "spiritual_name": db_user["spiritual_name"],
                "current_land": db_user["current_land"],
                "journey_streak": db_user["journey_streak"],
                "access_token": token,
                "token_type": "bearer"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

# Practice endpoints
@app.post("/practices/complete")
@limiter.limit("20/minute")
async def complete_practice(request: Request, completion: PracticeCompletion, user_email: str = Depends(get_current_user)):
    try:
        with get_db_connection() as conn:
            # Get user ID
            user = conn.execute("SELECT id FROM users WHERE email = ?", (user_email,)).fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Record completion
            conn.execute(
                """INSERT INTO practice_completions (user_id, practice_id, notes, duration_minutes) 
                   VALUES (?, ?, ?, ?)""",
                (user["id"], completion.practice_id, completion.notes, completion.duration_minutes)
            )
            
            # Update land progress
            practice = next((p for p in HEALING_PRACTICES if p["id"] == completion.practice_id), None)
            if practice:
                # Get existing progress or insert new
                progress = conn.execute(
                    "SELECT practices_completed, total_duration FROM user_land_progress WHERE user_id = ? AND land_id = ?",
                    (user["id"], practice["land"])
                ).fetchone()
                
                if progress:
                    conn.execute(
                        """UPDATE user_land_progress 
                           SET practices_completed = ?, total_duration = ?, last_visited = CURRENT_TIMESTAMP
                           WHERE user_id = ? AND land_id = ?""",
                        (progress["practices_completed"] + 1, progress["total_duration"] + completion.duration_minutes, 
                         user["id"], practice["land"])
                    )
                else:
                    conn.execute(
                        "INSERT INTO user_land_progress (user_id, land_id, practices_completed, total_duration) VALUES (?, ?, 1, ?)",
                        (user["id"], practice["land"], completion.duration_minutes)
                    )
            
            # Update user streak and last practice
            conn.execute(
                "UPDATE users SET last_practice_at = ?, journey_streak = journey_streak + 1 WHERE id = ?",
                (datetime.now(timezone.utc), user["id"])
            )
            
            conn.commit()
            
            # Get updated stats
            total_practices = conn.execute(
                "SELECT COUNT(*) as count FROM practice_completions WHERE user_id = ?", (user["id"],)
            ).fetchone()["count"]
            
            land_progress = conn.execute(
                "SELECT land_id, practices_completed, total_duration FROM user_land_progress WHERE user_id = ?",
                (user["id"],)
            ).fetchall()
            
            return {
                "message": "Practice completed with blessings",
                "total_practices": total_practices,
                "land_progress": [
                    {
                        "land": FOUR_LANDS[progress["land_id"]]["name"],
                        "practices_completed": progress["practices_completed"],
                        "total_duration": progress["total_duration"],
                        "symbol": FOUR_LANDS[progress["land_id"]]["symbol"]
                    }
                    for progress in land_progress
                ],
                "cultural_blessing": "May your journey through the lands bring healing and wisdom"
            }
            
    except Exception as e:
        logger.error(f"Practice completion error: {e}")
        raise HTTPException(status_code=500, detail="Failed to record practice")

@app.get("/user/progress")
async def get_user_progress(user_email: str = Depends(get_current_user)):
    try:
        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT id, spiritual_name, current_land, journey_streak, last_practice_at FROM users WHERE email = ?",
                (user_email,)
            ).fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get practice statistics
            total_practices = conn.execute(
                "SELECT COUNT(*) as count FROM practice_completions WHERE user_id = ?", (user["id"],)
            ).fetchone()["count"]
            
            land_progress = conn.execute(
                """SELECT land_id, practices_completed, total_duration 
                   FROM user_land_progress WHERE user_id = ?""",
                (user["id"],)
            ).fetchall()
            
            recent_practices = conn.execute(
                """SELECT practice_id, completed_at, duration_minutes 
                   FROM practice_completions 
                   WHERE user_id = ? 
                   ORDER BY completed_at DESC 
                   LIMIT 5""",
                (user["id"],)
            ).fetchall()
            
            return {
                "spiritual_name": user["spiritual_name"],
                "current_land": FOUR_LANDS[user["current_land"]],
                "journey_streak": user["journey_streak"],
                "total_practices": total_practices,
                "land_progress": [
                    {
                        "land": FOUR_LANDS[progress["land_id"]],
                        "practices_completed": progress["practices_completed"],
                        "total_duration": progress["total_duration"]
                    }
                    for progress in land_progress
                ],
                "recent_practices": [
                    {
                        "practice_id": practice["practice_id"],
                        "completed_at": practice["completed_at"],
                        "duration_minutes": practice["duration_minutes"]
                    }
                    for practice in recent_practices
                ],
                "cultural_message": "Your journey through the Four Lands is honored and witnessed"
            }
            
    except Exception as e:
        logger.error(f"Progress retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve progress")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
