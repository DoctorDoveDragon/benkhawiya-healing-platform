import sqlite3
import os
from contextlib import contextmanager

@contextmanager 
def get_db_connection():
    """Initialize SQLite database connection"""
    conn = sqlite3.connect('benkhawiya.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_tables():
    """Initialize all database tables"""
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
    print("✅ SQLite database tables initialized successfully!")

if __name__ == "__main__":
    init_tables()
    print("🚀 Database ready! Now run: python3 main.py")
