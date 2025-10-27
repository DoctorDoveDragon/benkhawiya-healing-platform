from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
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
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
database_pool = None

async def startup_db():
    """Initialize database connection on startup"""
    global database_pool
    try:
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            # Fix URL format if needed
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            
            database_pool = await asyncpg.create_pool(
                database_url,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            await init_tables()
            logger.info("✅ Database connection established successfully")
        else:
            logger.warning("⚠️ DATABASE_URL not set - running in memory mode")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")

async def shutdown_db():
    """Close database connection on shutdown"""
    global database_pool
    if database_pool:
        await database_pool.close()
        logger.info("🔌 Database connection closed")

async def init_tables():
    """Initialize database tables"""
    try:
        async with database_pool.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
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
            
            logger.info("✅ Database tables initialized successfully")
    except Exception as e:
        logger.error(f"❌ Table initialization failed: {e}")

# Lifespan context manager (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await startup_db()
    yield
    # Shutdown
    await shutdown_db()

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Benkhawiya Healing Platform",
    description="Complete ancestral spiritual healing system through the Four Lands",
    version="3.0.0",
    lifespan=lifespan
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

# CORRECTED COSMOLOGY - Four Lands: White, Black, Red, Green
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

# Routes
@app.get("/")
async def root():
    return {
        "message": "Benkhawiya Healing Platform", 
        "version": "3.0.0", 
        "status": "active",
        "cosmology": "Four Lands: White, Black, Red, Green",
        "language": "Benkhawiya",
        "database_status": "connected" if database_pool else "memory_mode"
    }

@app.get("/health")
async def health():
    db_status = "connected" if database_pool else "memory_mode"
    return {
        "status": "healthy", 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "benkhawiya-healing-platform",
        "database": db_status,
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
    if not database_pool:
        raise HTTPException(
            status_code=503, 
            detail="Database unavailable. Please add PostgreSQL service in Railway dashboard."
        )
    
    try:
        async with database_pool.acquire() as conn:
            existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", user.email)
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            hashed_password = get_password_hash(user.password)
            user_id = await conn.fetchval(
                "INSERT INTO users (email, spiritual_name, password_hash) VALUES ($1, $2, $3) RETURNING id",
                user.email, user.spiritual_name, hashed_password
            )
            
            for land_id in FOUR_LANDS.keys():
                await conn.execute(
                    "INSERT INTO user_land_progress (user_id, land_id) VALUES ($1, $2)",
                    user_id, land_id
                )
            
            token = create_access_token({"sub": user.email})
            
            return {
                "message": "Welcome to the Benkhawiya journey through the Four Lands",
                "user_id": user_id,
                "spiritual_name": user.spiritual_name,
                "access_token": token,
                "token_type": "bearer",
                "cosmology": "Four Lands: White, Black, Red, Green"
            }
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, user: UserLogin):
    if not database_pool:
        raise HTTPException(
            status_code=503, 
            detail="Database unavailable. Please add PostgreSQL service in Railway dashboard."
        )
    
    try:
        async with database_pool.acquire() as conn:
            db_user = await conn.fetchrow(
                "SELECT id, email, spiritual_name, password_hash, current_land, journey_streak FROM users WHERE email = $1",
                user.email
            )
            
            if not db_user or not verify_password(user.password, db_user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            await conn.execute(
                "UPDATE users SET last_practice_at = $1 WHERE id = $2",
                datetime.now(timezone.utc), db_user["id"]
            )
            
            token = create_access_token({"sub": db_user["email"]})
            
            return {
                "message": "Welcome back to your healing journey through the Four Lands",
                "user_id": db_user["id"],
                "spiritual_name": db_user["spiritual_name"],
                "current_land": FOUR_LANDS[db_user["current_land"]],
                "journey_streak": db_user["journey_streak"],
                "access_token": token,
                "token_type": "bearer"
            }
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
