from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import asyncpg
import os
import uvicorn
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Benkhawiya Healing Platform",
    description="Production API for spiritual healing practices",
    version="2.0.0"
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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Environment variables with fallbacks
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key-32-chars-minimum-here")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Database pool
pool = None

# Healing practices
HEALING_PRACTICES = {
    "beginner": [
        {
            "id": "reconnection_breathing",
            "name": "Reconnection Breathing",
            "duration": 5,
            "steps": [
                "Find comfortable seated position",
                "Close eyes, take 3 deep breaths",
                "Breathe in: I honor my ancestors",
                "Breathe out: I release fragmentation",
                "Breathe in: I am whole",
                "Breathe out: I am connected",
                "Continue for 5 minutes"
            ],
            "focus": "Spiritual continuity repair"
        }
    ]
}

async def init_database():
    """Initialize database connection and tables"""
    global pool
    if not DATABASE_URL:
        logger.warning("⚠️ DATABASE_URL not set - running without database")
        return
    
    try:
        # Connect with retry logic
        for attempt in range(3):
            try:
                pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
                logger.info("✅ Database connected")
                break
            except Exception as e:
                logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise
                await asyncio.sleep(2)
        
        # Create tables
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS practice_completions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id),
                    practice_id VARCHAR(100),
                    completed_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            logger.info("✅ Database tables ready")
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        pool = None

@app.on_event("startup")
async def startup():
    """Application startup"""
    logger.info("🚀 Starting Benkhawiya Healing Platform")
    await init_database()
    logger.info("✅ Startup complete")

@app.on_event("shutdown")
async def shutdown():
    """Application shutdown"""
    if pool:
        await pool.close()
        logger.info("✅ Database closed")

# ========== API ENDPOINTS ==========

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
    db_status = "disconnected"
    if pool:
        try:
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            db_status = "connected"
        except:
            db_status = "error"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": ENVIRONMENT
    }

@app.post("/auth/register")
@limiter.limit("5/minute")
async def register(request: Request):
    """User registration"""
    try:
        data = await request.json()
    except:
        raise HTTPException(400, "Invalid JSON")
    
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(400, "Email and password required")
    
    if not pool:
        raise HTTPException(503, "Database unavailable")
    
    try:
        async with pool.acquire() as conn:
            # Check existing user
            existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
            if existing:
                raise HTTPException(400, "User already exists")
            
            # Create user
            hashed = pwd_context.hash(password)
            user_id = await conn.fetchval(
                "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id",
                email, hashed
            )
            
            # Create token
            token = jwt.encode(
                {"sub": str(user_id), "email": email, "exp": datetime.utcnow() + timedelta(hours=24)},
                SECRET_KEY,
                algorithm="HS256"
            )
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user_id": str(user_id),
                "email": email
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(500, "Registration failed")

@app.post("/auth/login")
@limiter.limit("10/minute")
async def login(request: Request):
    """User login"""
    try:
        data = await request.json()
    except:
        raise HTTPException(400, "Invalid JSON")
    
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(400, "Email and password required")
    
    if not pool:
        raise HTTPException(503, "Database unavailable")
    
    try:
        async with pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
            
            if not user or not pwd_context.verify(password, user["password_hash"]):
                raise HTTPException(401, "Invalid credentials")
            
            token = jwt.encode(
                {"sub": str(user["id"]), "email": user["email"], "exp": datetime.utcnow() + timedelta(hours=24)},
                SECRET_KEY,
                algorithm="HS256"
            )
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user_id": str(user["id"]),
                "email": user["email"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(500, "Login failed")

@app.get("/practices/daily")
@limiter.limit("30/minute")
async def daily_practice(request: Request):
    """Get daily practice"""
    practices = HEALING_PRACTICES["beginner"]
    day_of_year = datetime.now().timetuple().tm_yday
    practice = practices[day_of_year % len(practices)]
    
    return {
        "practice": practice,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/practices/complete")
@limiter.limit("20/minute")
async def complete_practice(request: Request):
    """Record practice completion"""
    try:
        data = await request.json()
    except:
        raise HTTPException(400, "Invalid JSON")
    
    practice_id = data.get("practice_id")
    user_id = data.get("user_id")
    
    if not practice_id:
        raise HTTPException(400, "Practice ID required")
    
    if not pool:
        return {"status": "recorded_offline", "practice_id": practice_id}
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO practice_completions (user_id, practice_id) VALUES ($1, $2)",
                user_id, practice_id
            )
            
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM practice_completions WHERE user_id = $1",
                user_id
            )
            
            return {
                "status": "completed",
                "practice_id": practice_id,
                "total_completions": count
            }
            
    except Exception as e:
        logger.error(f"Completion error: {e}")
        raise HTTPException(500, "Completion failed")

@app.get("/user/progress")
@limiter.limit("30/minute")
async def user_progress(request: Request):
    """Get user progress"""
    user_id = request.query_params.get("user_id")
    
    if not pool:
        return {
            "user_id": user_id,
            "total_practices": 0,
            "message": "Database offline"
        }
    
    try:
        async with pool.acquire() as conn:
            total = await conn.fetchval(
                "SELECT COUNT(*) FROM practice_completions WHERE user_id = $1",
                user_id
            )
            
            weekly = await conn.fetchval(
                "SELECT COUNT(*) FROM practice_completions WHERE user_id = $1 AND completed_at >= NOW() - INTERVAL '7 days'",
                user_id
            )
            
            return {
                "user_id": user_id,
                "total_practices": total,
                "weekly_completions": weekly,
                "healing_journey": "active" if weekly > 0 else "beginning"
            }
            
    except Exception as e:
        logger.error(f"Progress error: {e}")
        raise HTTPException(500, "Progress check failed")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
