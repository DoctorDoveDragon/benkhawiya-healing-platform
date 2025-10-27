import sqlite3
import os
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """Get database connection - uses SQLite if no PostgreSQL available"""
    # Try PostgreSQL first if DATABASE_URL is set
    db_url = os.getenv("DATABASE_URL")
    
    if db_url and db_url.startswith("postgresql://"):
        import asyncpg
        # PostgreSQL connection would go here
        yield None
    else:
        # Fallback to SQLite
        conn = sqlite3.connect('benkhawiya.db')
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

async def init_simple_tables():
    """Initialize simple SQLite tables"""
    with get_db_connection() as conn:
        if conn:
            # Users table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    spiritual_name VARCHAR(255),
                    password_hash VARCHAR(255) NOT NULL,
                    current_land VARCHAR(50) DEFAULT 'white_land',
                    journey_streak INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            
            conn.commit()
            print("SQLite tables initialized")

if __name__ == "__main__":
    init_simple_tables()
