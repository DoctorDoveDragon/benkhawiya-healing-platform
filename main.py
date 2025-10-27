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
import asyncpg
import os
import uvicorn
import logging
from jose import JWTError, jwt  # CORRECT IMPORT
from passlib.context import CryptContext
import asyncio
from pydantic import BaseModel
import json

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
database = None

# CULTURAL FOUNDATION: THE FOUR LANDS
FOUR_LANDS = {
    "eastern_land": {
        "name": "Land of New Beginnings",
        "element": "Air",
        "direction": "East", 
        "teaching": "Wisdom and Clarity",
        "animal": "Eagle",
        "color": "Gold",
        "symbol": "🦅",
        "practice": "Morning meditation for clear vision",
        "blessing": "May the Eastern winds bring you clarity and new beginnings"
    },
    "southern_land": {
        "name": "Land of Growth", 
        "element": "Fire",
        "direction": "South",
        "teaching": "Passion and Transformation",
        "animal": "Lion",
        "color": "Red",
        "symbol": "🦁",
        "practice": "Energy work for personal power",
        "blessing": "May the Southern fire transform your challenges into strength"
    },
    "western_land": {
        "name": "Land of Introspection",
        "element": "Water", 
        "direction": "West",
        "teaching": "Emotional Healing",
        "animal": "Bear",
        "color": "Blue",
        "symbol": "🐻",
        "practice": "Evening reflection for emotional balance",
        "blessing": "May the Western waters heal your heart and cleanse your spirit"
    },
    "northern_land": {
        "name": "Land of Ancestral Wisdom",
        "element": "Earth",
        "direction": "North",
        "teaching": "Foundation and Tradition",
        "animal": "Buffalo",
        "color": "Green", 
        "symbol": "🐃",
        "practice": "Ancestral connection practices",
        "blessing": "May the Northern earth connect you to ancestral wisdom and guidance"
    }
}

HEALING_PRACTICES = [
    {
        "id": "eagle_vision",
        "name": "Eastern Gate: Eagle Vision Meditation",
        "land": "eastern_land",
        "description": "Connect with the Eastern Land's wisdom through elevated perspective",
        "duration": 15,
        "difficulty": "beginner",
        "steps": [
            "Face East towards new beginnings",
            "Visualize golden light of dawn", 
            "Call upon Eagle's far-seeing vision",
            "Receive clarity for your path ahead",
            "Offer gratitude for new perspectives"
        ],
        "cultural_context": "The Eastern Land teaches us to see beyond immediate circumstances to the larger journey of our soul"
    },
    {
        "id": "lion_heart",
        "name": "Southern Fire: Lion Heart Activation",
        "land": "southern_land", 
        "description": "Ignite your inner fire with Southern Land's transformative energy",
        "duration": 20,
        "difficulty": "intermediate",
        "steps": [
            "Face South with open heart",
            "Feel the red fire of passion rising",
            "Channel Lion's courage and royal presence", 
            "Transform personal challenges into spiritual power",
            "Claim your sacred authority"
        ],
        "cultural_context": "The Southern Land reminds us that our greatest trials forge our strongest spirit and purpose"
    },
    {
        "id": "bear_healing",
        "name": "Western Waters: Bear Heart Healing",
        "land": "western_land",
        "description": "Journey inward with Western Land's healing waters for emotional restoration",
        "duration": 25,
        "difficulty": "intermediate",
        "steps": [
            "Face West at sunset time",
            "Welcome blue healing waters around you",
            "Enter Bear's sacred cave of introspection",
            "Release emotional burdens to the cleansing waters",
            "Embrace deep emotional renewal"
        ],
        "cultural_context": "The Western Land teaches that true warrior strength comes from emotional honesty and healing vulnerability"
    },
    {
        "id": "buffalo_ancestors",
        "name": "Northern Roots: Buffalo Ancestral Connection", 
        "land": "northern_land",
        "description": "Ground in ancestral wisdom through Northern Land's enduring stability",
        "duration": 30,
        "difficulty": "advanced",
        "steps": [
            "Face North under the starry sky",
            "Feel green earth energy rising through you",
            "Connect with Buffalo's generous and enduring spirit",
            "Receive ancestral guidance and blessings",
            "Commit to walking in sacred manner"
        ],
        "cultural_context": "The Northern Land reminds us we walk on the shoulders of ancestors who guide our path and await our honoring"
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

class UserProfile(BaseModel):
    spiritual_name: str
    current_land: str = "eastern_land"
    journey_streak: int = 0

# Database functions
async def get_database():
    global database
    if database is None:
        try:
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                database = await asyncpg.create_pool(database_url)
                await init_tables()
                logger.info("Database connection established")
            else:
                logger.warning("DATABASE_URL not set - running in memory mode")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
    return database

async def init_tables():
    """Initialize database tables"""
    try:
        async with database.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    spiritual_name VARCHAR(255),
                    password_hash VARCHAR(255) NOT NULL,
                    current_land VARCHAR(50) DEFAULT 'eastern_land',
                    journey_streak INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_practice_at TIMESTAMP
                )
            ''')
            
            # Practice completions
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS practice_completions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    practice_id VARCHAR(100) NOT NULL,
                    notes TEXT,
                    duration_minutes INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User progress
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_land_progress (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    land_id VARCHAR(50) NOT NULL,
                    practices_completed INTEGER DEFAULT 0,
                    total_duration INTEGER DEFAULT 0,
                    last_visited TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Table initialization failed: {e}")

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

# Application lifespan
@app.on_event("startup")
async def startup_event():
    await get_database()
    logger.info("Benkhawiya Healing Platform started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    if database:
        await database.close()
        logger.info("Database connection closed")

# Routes
@app.get("/")
async def root():
    return {"message": "Benkhawiya Healing Platform", "version": "3.0.0", "status": "active"}

@app.get("/health")
async def health():
    db_status = "connected" if database else "disconnected"
    return {
        "status": "healthy", 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "benkhawiya-healing-platform",
        "database": db_status,
        "cultural_foundation": "Four Lands Tradition"
    }

# Cultural endpoints
@app.get("/four-lands")
async def get_four_lands():
    return FOUR_LANDS

@app.get("/practices/daily")
async def daily_practice():
    """Get today's practice based on day of year"""
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
    db = await get_database()
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        async with db.acquire() as conn:
            # Check if user exists
            existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", user.email)
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # Create user
            hashed_password = get_password_hash(user.password)
            user_id = await conn.fetchval(
                "INSERT INTO users (email, spiritual_name, password_hash) VALUES ($1, $2, $3) RETURNING id",
                user.email, user.spiritual_name, hashed_password
            )
            
            # Initialize land progress
            for land_id in FOUR_LANDS.keys():
                await conn.execute(
                    "INSERT INTO user_land_progress (user_id, land_id) VALUES ($1, $2)",
                    user_id, land_id
                )
            
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
    db = await get_database()
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        async with db.acquire() as conn:
            db_user = await conn.fetchrow(
                "SELECT id, email, spiritual_name, password_hash, current_land, journey_streak FROM users WHERE email = $1",
                user.email
            )
            
            if not db_user or not verify_password(user.password, db_user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Update last login
            await conn.execute(
                "UPDATE users SET last_practice_at = $1 WHERE id = $2",
                datetime.now(timezone.utc), db_user["id"]
            )
            
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
    db = await get_database()
    if not db:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    try:
        async with db.acquire() as conn:
            # Get user ID
            user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", user_email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Record completion
            await conn.execute(
                """INSERT INTO practice_completions (user_id, practice_id, notes, duration_minutes) 
                   VALUES ($1, $2, $3, $4)""",
                user["id"], completion.practice_id, completion.notes, completion.duration_minutes
            )
            
            # Update land progress
            practice = next((p for p in HEALING_PRACTICES if p["id"] == completion.practice_id), None)
            if practice:
                await conn.execute(
                    """INSERT INTO user_land_progress (user_id, land_id, practices_completed, total_duration) 
                       VALUES ($1, $2, 1, $3)
                       ON CONFLICT (user_id, land_id) 
                       DO UPDATE SET 
                         practices_completed = user_land_progress.practices_completed + 1,
                         total_duration = user_land_progress.total_duration + $3,
                         last_visited = CURRENT_TIMESTAMP""",
                    user["id"], practice["land"], completion.duration_minutes
                )
            
            # Update user streak and last practice
            await conn.execute(
                "UPDATE users SET last_practice_at = $1, journey_streak = journey_streak + 1 WHERE id = $2",
                datetime.now(timezone.utc), user["id"]
            )
            
            # Get updated stats
            total_practices = await conn.fetchval(
                "SELECT COUNT(*) FROM practice_completions WHERE user_id = $1", user["id"]
            )
            
            land_progress = await conn.fetch(
                "SELECT land_id, practices_completed, total_duration FROM user_land_progress WHERE user_id = $1",
                user["id"]
            )
            
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
    db = await get_database()
    if not db:
        return {"message": "Database offline - progress tracking unavailable"}
    
    try:
        async with db.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT id, spiritual_name, current_land, journey_streak, last_practice_at FROM users WHERE email = $1",
                user_email
            )
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get practice statistics
            total_practices = await conn.fetchval(
                "SELECT COUNT(*) FROM practice_completions WHERE user_id = $1", user["id"]
            )
            
            land_progress = await conn.fetch(
                """SELECT land_id, practices_completed, total_duration 
                   FROM user_land_progress WHERE user_id = $1""",
                user["id"]
            )
            
            recent_practices = await conn.fetch(
                """SELECT practice_id, completed_at, duration_minutes 
                   FROM practice_completions 
                   WHERE user_id = $1 
                   ORDER BY completed_at DESC 
                   LIMIT 5""",
                user["id"]
            )
            
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
                "recent_practices": recent_practices,
                "cultural_message": "Your journey through the Four Lands is honored and witnessed"
            }
            
    except Exception as e:
        logger.error(f"Progress retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve progress")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
