from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import asyncpg
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import jwt
from passlib.context import CryptContext
import logging
import time

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Benkhawiya Healing Platform API",
    description="Production API for spiritual continuity healing practices",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limiting - PRODUCTION SETTINGS
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database connection pool
pool: Optional[asyncpg.Pool] = None

# Healing practices data
HEALING_PRACTICES = {
    "beginner": [
        {
            "id": "reconnection_breathing",
            "name": "Reconnection Breathing",
            "duration": 5,
            "steps": [
                "Find a comfortable seated position",
                "Close your eyes and take 3 deep breaths",
                "Breathe in: I honor my ancestors",
                "Breathe out: I release fragmentation", 
                "Breathe in: I am whole",
                "Breathe out: I am connected",
                "Continue for 5 minutes, maintaining awareness"
            ],
            "focus": "Spiritual continuity repair",
            "benefits": ["Grounding", "Ancestral connection", "Present moment awareness"]
        },
        {
            "id": "ancestral_grounding",
            "name": "Ancestral Grounding",
            "duration": 7,
            "steps": [
                "Stand or sit with feet firmly on the ground",
                "Feel your connection to the earth beneath you",
                "Imagine roots extending from your feet to ancestral lands",
                "Draw strength and wisdom from those who came before",
                "Feel the continuity of life through your being",
                "Express gratitude for this sacred connection"
            ],
            "focus": "Cognitive discontinuity healing", 
            "benefits": ["Stability", "Cultural continuity", "Personal identity strength"]
        }
    ],
    "intermediate": [
        {
            "id": "identity_integration",
            "name": "Identity Integration Practice", 
            "duration": 10,
            "steps": [
                "Sit comfortably with journal and pen nearby",
                "Acknowledge the different fragments of your identity",
                "Welcome each part with compassion and understanding", 
                "Weave them into a cohesive whole through visualization",
                "Honor the beauty and strength of your complete self",
                "Write down insights, commitments, and affirmations"
            ],
            "focus": "Identity fragmentation repair",
            "benefits": ["Self-acceptance", "Identity coherence", "Personal empowerment"]
        }
    ],
    "advanced": [
        {
            "id": "intergenerational_healing",
            "name": "Intergenerational Healing Meditation",
            "duration": 15,
            "steps": [
                "Create a sacred space with intention",
                "Connect with your ancestral lineage through breath",
                "Visualize healing light passing through generations", 
                "Release inherited trauma with compassion",
                "Embrace inherited strengths and wisdom",
                "Set intentions for future generations"
            ],
            "focus": "Transgenerational healing work",
            "benefits": ["Lineage healing", "Trauma release", "Generational blessing"]
        }
    ]
}

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    global pool
    logger.info("🚀 Starting Benkhawiya Healing Platform API")
    
    try:
        pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        await initialize_database()
        logger.info("✅ Database connection established successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    if pool:
        await pool.close()
        logger.info("✅ Database connection pool closed")

async def initialize_database():
    """Initialize database tables"""
    try:
        async with pool.acquire() as conn:
            # Users table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    user_level VARCHAR(20) DEFAULT 'beginner',
                    healing_focus TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            # Practice completions
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS practice_completions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    practice_id VARCHAR(100) NOT NULL,
                    completed_at TIMESTAMPTZ DEFAULT NOW(),
                    notes TEXT,
                    duration_minutes INTEGER
                )
            ''')
            
            # Healing progress metrics
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS healing_progress (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
                    date DATE DEFAULT CURRENT_DATE,
                    coherence_score INTEGER CHECK (coherence_score >= 1 AND coherence_score <= 10),
                    continuity_feeling INTEGER CHECK (continuity_feeling >= 1 AND continuity_feeling <= 10),
                    notes TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            
            # Create indexes for performance
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_practice_completions_user_id 
                ON practice_completions(user_id, completed_at DESC)
            ''')
            
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_healing_progress_user_date 
                ON healing_progress(user_id, date DESC)
            ''')
            
        logger.info("✅ Database initialization completed")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

# Security utilities
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1 AND is_active = TRUE", user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found or inactive")
        return user

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {process_time:.3f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# ========== API ENDPOINTS ==========

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Benkhawiya Healing Platform API",
        "version": "2.0.0", 
        "status": "active",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Railway (60-second checks)
    Returns comprehensive system health status
    """
    try:
        # Test database connection
        async with pool.acquire() as conn:
            db_status = await conn.fetchval("SELECT 1")
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "version": "2.0.0",
            "environment": settings.environment
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy - database connection failed"
        )

@app.post("/auth/register")
@limiter.limit("5/minute")
async def register_user(request: Request, data: dict):
    """Register a new user account"""
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    try:
        async with pool.acquire() as conn:
            # Check if user already exists
            existing_user = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1", email
            )
            if existing_user:
                raise HTTPException(status_code=400, detail="User with this email already exists")
            
            # Create new user
            hashed_password = hash_password(password)
            user_id = await conn.fetchval(
                """INSERT INTO users (email, password_hash) 
                VALUES ($1, $2) RETURNING id""",
                email, hashed_password
            )
            
            # Create access token
            access_token = create_access_token({"sub": str(user_id), "email": email})
            
            logger.info(f"New user registered: {email}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": str(user_id),
                "email": email,
                "message": "Registration successful"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/auth/login") 
@limiter.limit("10/minute")
async def login_user(request: Request, data: dict):
    """Authenticate user and return access token"""
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    try:
        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1 AND is_active = TRUE", email
            )
            
            if not user or not verify_password(password, user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # Create access token
            access_token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
            
            logger.info(f"User logged in: {email}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer", 
                "user_id": str(user["id"]),
                "email": user["email"],
                "user_level": user["user_level"]
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/practices")
@limiter.limit("30/minute")
async def get_all_practices(request: Request, user: dict = Depends(get_current_user)):
    """Get all available practices for user's level"""
    user_level = user["user_level"]
    practices = HEALING_PRACTICES.get(user_level, HEALING_PRACTICES["beginner"])
    
    return {
        "practices": practices,
        "user_level": user_level,
        "total_practices": len(practices)
    }

@app.get("/practices/daily")
@limiter.limit("30/minute") 
async def get_daily_practice(request: Request, user: dict = Depends(get_current_user)):
    """Get today's personalized healing practice"""
    user_id = user["id"]
    user_level = user["user_level"]
    
    try:
        async with pool.acquire() as conn:
            # Get practices for user level
            practices = HEALING_PRACTICES.get(user_level, HEALING_PRACTICES["beginner"])
            
            # Get recent practices to avoid repetition
            recent_practices = await conn.fetch(
                """SELECT practice_id FROM practice_completions 
                WHERE user_id = $1 AND completed_at >= NOW() - INTERVAL '3 days'
                ORDER BY completed_at DESC LIMIT 5""",
                user_id
            )
            recent_ids = [p["practice_id"] for p in recent_practices]
            
            # Filter out recently completed practices
            available_practices = [p for p in practices if p["id"] not in recent_ids]
            if not available_practices:
                available_practices = practices  # Fallback to all practices
            
            # Select practice based on day of year for consistency
            day_of_year = datetime.now().timetuple().tm_yday
            practice = available_practices[day_of_year % len(available_practices)]
            
            logger.info(f"Selected practice {practice['id']} for user {user_id}")
            
            return {
                "practice": practice,
                "timestamp": datetime.utcnow().isoformat(),
                "user_level": user_level,
                "suggested_time": "morning"
            }
            
    except Exception as e:
        logger.error(f"Error getting daily practice: {e}")
        raise HTTPException(status_code=500, detail="Failed to get daily practice")

@app.post("/practices/complete")
@limiter.limit("20/minute")
async def complete_practice(request: Request, data: dict, user: dict = Depends(get_current_user)):
    """Record practice completion"""
    user_id = user["id"]
    practice_id = data.get("practice_id")
    notes = data.get("notes", "")
    
    if not practice_id:
        raise HTTPException(status_code=400, detail="Practice ID is required")
    
    # Validate practice exists
    practice_exists = any(
        p["id"] == practice_id 
        for level in HEALING_PRACTICES.values() 
        for p in level
    )
    
    if not practice_exists:
        raise HTTPException(status_code=400, detail="Invalid practice ID")
    
    try:
        async with pool.acquire() as conn:
            # Get practice duration
            practice_duration = next(
                p["duration"] for level in HEALING_PRACTICES.values() 
                for p in level if p["id"] == practice_id
            )
            
            # Record completion
            await conn.execute(
                """INSERT INTO practice_completions 
                (user_id, practice_id, notes, duration_minutes) 
                VALUES ($1, $2, $3, $4)""",
                user_id, practice_id, notes, practice_duration
            )
            
            # Get updated completion count
            completions_count = await conn.fetchval(
                "SELECT COUNT(*) FROM practice_completions WHERE user_id = $1",
                user_id
            )
            
            logger.info(f"Practice {practice_id} completed by user {user_id}")
            
            return {
                "status": "completed", 
                "practice_id": practice_id,
                "total_completions": completions_count,
                "completion_time": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error completing practice: {e}")
        raise HTTPException(status_code=500, detail="Failed to record practice completion")

@app.get("/user/profile")
@limiter.limit("30/minute")
async def get_user_profile(request: Request, user: dict = Depends(get_current_user)):
    """Get user profile information"""
    return {
        "user_id": str(user["id"]),
        "email": user["email"],
        "user_level": user["user_level"],
        "healing_focus": user["healing_focus"],
        "created_at": user["created_at"].isoformat()
    }

@app.get("/user/progress")
@limiter.limit("30/minute")
async def get_user_progress(request: Request, user: dict = Depends(get_current_user)):
    """Get comprehensive user progress and statistics"""
    user_id = user["id"]
    
    try:
        async with pool.acquire() as conn:
            # Basic completion stats
            total_practices = await conn.fetchval(
                "SELECT COUNT(*) FROM practice_completions WHERE user_id = $1",
                user_id
            )
            
            weekly_completions = await conn.fetchval(
                """SELECT COUNT(*) FROM practice_completions 
                WHERE user_id = $1 AND completed_at >= NOW() - INTERVAL '7 days'""",
                user_id
            )
            
            monthly_completions = await conn.fetchval(
                """SELECT COUNT(*) FROM practice_completions 
                WHERE user_id = $1 AND completed_at >= NOW() - INTERVAL '30 days'""",
                user_id
            )
            
            # Streak calculation
            streak = await calculate_streak(conn, user_id)
            
            # Recent practices
            recent_practices = await conn.fetch(
                """SELECT practice_id, completed_at, notes 
                FROM practice_completions 
                WHERE user_id = $1 
                ORDER BY completed_at DESC 
                LIMIT 5""",
                user_id
            )
            
            progress_data = {
                "user_id": str(user_id),
                "total_practices": total_practices,
                "weekly_completions": weekly_completions,
                "monthly_completions": monthly_completions,
                "current_streak": streak,
                "recent_practices": [
                    {
                        "practice_id": p["practice_id"],
                        "completed_at": p["completed_at"].isoformat(),
                        "notes": p["notes"]
                    } for p in recent_practices
                ],
                "healing_journey": "active" if weekly_completions > 0 else "beginning",
                "message": "Every practice moves you toward wholeness and continuity"
            }
            
            return progress_data
            
    except Exception as e:
        logger.error(f"Error getting user progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user progress")

async def calculate_streak(conn, user_id: str) -> int:
    """Calculate current streak of consecutive days with practice"""
    completions = await conn.fetch(
        """SELECT DISTINCT DATE(completed_at) as date 
        FROM practice_completions 
        WHERE user_id = $1 
        ORDER BY date DESC""",
        user_id
    )
    
    streak = 0
    current_date = datetime.now().date()
    
    for completion in completions:
        completion_date = completion["date"]
        expected_date = current_date - timedelta(days=streak)
        
        if completion_date == expected_date:
            streak += 1
        elif completion_date == current_date - timedelta(days=streak + 1):
            # Allow for one missed day in streak calculation
            streak += 1
        else:
            break
            
    return streak

@app.post("/user/progress/metrics")
@limiter.limit("20/minute")
async def record_progress_metrics(request: Request, data: dict, user: dict = Depends(get_current_user)):
    """Record user healing progress metrics"""
    user_id = user["id"]
    coherence_score = data.get("coherence_score")
    continuity_feeling = data.get("continuity_feeling")
    notes = data.get("notes", "")
    
    if coherence_score is None or continuity_feeling is None:
        raise HTTPException(status_code=400, detail="Both coherence_score and continuity_feeling are required")
    
    if not (1 <= coherence_score <= 10) or not (1 <= continuity_feeling <= 10):
        raise HTTPException(status_code=400, detail="Scores must be between 1 and 10")
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO healing_progress 
                (user_id, coherence_score, continuity_feeling, notes) 
                VALUES ($1, $2, $3, $4)""",
                user_id, coherence_score, continuity_feeling, notes
            )
            
            return {
                "status": "recorded",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Progress metrics recorded successfully"
            }
            
    except Exception as e:
        logger.error(f"Error recording progress metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to record progress metrics")

@app.get("/user/streak")
@limiter.limit("30/minute")
async def get_user_streak(request: Request, user: dict = Depends(get_current_user)):
    """Get detailed streak information"""
    user_id = user["id"]
    
    try:
        async with pool.acquire() as conn:
            streak = await calculate_streak(conn, user_id)
            
            # Get streak history
            streak_history = await conn.fetch(
                """SELECT DATE(completed_at) as date, COUNT(*) as practices
                FROM practice_completions 
                WHERE user_id = $1 AND completed_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(completed_at)
                ORDER BY date DESC""",
                user_id
            )
            
            return {
                "current_streak": streak,
                "streak_history": [
                    {
                        "date": row["date"].isoformat(),
                        "practices": row["practices"]
                    } for row in streak_history
                ],
                "longest_streak": streak  # Simplified - would need more calculation in production
            }
            
    except Exception as e:
        logger.error(f"Error getting streak: {e}")
        raise HTTPException(status_code=500, detail="Failed to get streak information")

@app.put("/user/level")
@limiter.limit("10/minute")
async def update_user_level(request: Request, data: dict, user: dict = Depends(get_current_user)):
    """Update user level"""
    user_id = user["id"]
    new_level = data.get("user_level")
    
    valid_levels = ["beginner", "intermediate", "advanced"]
    if new_level not in valid_levels:
        raise HTTPException(status_code=400, detail="Invalid user level")
    
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE users SET user_level = $1, updated_at = NOW() WHERE id = $2",
                new_level, user_id
            )
            
            return {
                "status": "updated",
                "user_level": new_level,
                "message": "User level updated successfully"
            }
            
    except Exception as e:
        logger.error(f"Error updating user level: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user level")

# Error handlers
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return {
        "detail": "Internal server error",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    return {
        "detail": "Resource not found",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
