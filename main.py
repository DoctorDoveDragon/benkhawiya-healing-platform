from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime, timezone
import os
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Benkhawiya Healing Platform",
    description="Spiritual healing practices API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEALING_PRACTICES = [
    "Morning meditation: 15 minutes of mindful breathing",
    "Evening reflection: Gratitude journaling", 
    "Body scan relaxation technique",
    "Loving-kindness meditation for self and others",
    "Energy cleansing visualization"
]

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>Benkhawiya Healing Platform</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px;
                    background: #f5f5f5;
                    color: #333;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { color: #2c5530; }
                .practice { 
                    background: #f0f8ff; 
                    padding: 20px; 
                    margin: 20px 0;
                    border-left: 4px solid #4CAF50;
                    border-radius: 5px;
                }
                .api-link {
                    display: inline-block;
                    background: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 10px 5px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌿 Benkhawiya Healing Platform</h1>
                <p>Welcome to your spiritual healing journey</p>
                
                <div class="practice">
                    <h3>Today's Healing Practice</h3>
                    <div id="practice-content">Loading your daily practice...</div>
                </div>
                
                <div>
                    <h3>API Endpoints</h3>
                    <a class="api-link" href="/health">Health Check</a>
                    <a class="api-link" href="/docs">API Documentation</a>
                    <a class="api-link" href="/practices/daily">Daily Practice (JSON)</a>
                </div>
            </div>
            
            <script>
                // Fetch today's practice
                fetch('/practices/daily')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('practice-content').innerHTML = 
                            `<p><strong>${data.practice}</strong></p>
                             <small>Day ${data.day_of_year} of your healing journey</small>`;
                    })
                    .catch(error => {
                        document.getElementById('practice-content').innerHTML = 
                            '<p>Unable to load practice. Please try the API directly.</p>';
                    });
            </script>
        </body>
    </html>
    """

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "benkhawiya-healing-platform"
    }

@app.get("/practices/daily")
async def daily_practice():
    day_of_year = datetime.now().timetuple().tm_yday
    practice = HEALING_PRACTICES[day_of_year % len(HEALING_PRACTICES)]
    
    return {
        "practice": practice,
        "day_of_year": day_of_year,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
