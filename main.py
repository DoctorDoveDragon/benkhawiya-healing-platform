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
    description="Interactive spiritual healing practices",
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
    {
        "name": "Morning Meditation",
        "description": "15 minutes of mindful breathing for inner peace",
        "duration": 15,
        "steps": ["Find quiet space", "Sit comfortably", "Focus on breath", "Return gently"]
    },
    {
        "name": "Gratitude Journaling", 
        "description": "Evening reflection on daily blessings",
        "duration": 10,
        "steps": ["Get journal", "List 3 blessings", "Reflect on each", "Express thanks"]
    },
    {
        "name": "Body Scan Relaxation",
        "description": "Progressive relaxation technique for stress relief",
        "duration": 20,
        "steps": ["Lie down comfortably", "Start with toes", "Move upward slowly", "Release tension"]
    },
    {
        "name": "Loving-Kindness Meditation",
        "description": "Cultivate compassion for self and others",
        "duration": 15,
        "steps": ["Send love to self", "Send love to loved ones", "Send love to all beings", "Rest in compassion"]
    },
    {
        "name": "Energy Cleansing",
        "description": "Visualization technique for emotional balance",
        "duration": 10,
        "steps": ["Visualize white light", "Scan body for tension", "Release stagnant energy", "Fill with fresh energy"]
    }
]

@app.get("/", response_class=HTMLResponse)
async def interactive_homepage():
    return '''
    <html>
        <head>
            <title>Benkhawiya Healing Platform</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    padding: 30px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                }
                h1 { 
                    color: #fff;
                    text-align: center;
                    margin-bottom: 30px;
                }
                .practice-card {
                    background: rgba(255,255,255,0.2);
                    padding: 20px;
                    margin: 15px 0;
                    border-radius: 10px;
                    border-left: 5px solid #4CAF50;
                }
                .btn {
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 5px;
                }
                .btn:hover {
                    background: #45a049;
                }
                .loading {
                    color: #ffeb3b;
                    font-style: italic;
                }
                .completed {
                    color: #4CAF50;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌿 Benkhawiya Healing Platform</h1>
                <p>Welcome to your interactive spiritual healing journey</p>
                
                <div id="daily-practice">
                    <h2>Today's Healing Practice</h2>
                    <div id="practice-content" class="loading">Loading your daily practice...</div>
                    <button class="btn" onclick="startPractice()">Start Practice</button>
                    <button class="btn" onclick="completePractice()">Mark Complete</button>
                    <div id="practice-status"></div>
                </div>

                <div id="progress-section">
                    <h2>Your Healing Journey</h2>
                    <p>Completed practices: <span id="completed-count">0</span></p>
                    <button class="btn" onclick="viewAllPractices()">View All Practices</button>
                    <div id="all-practices" style="display:none;"></div>
                </div>
            </div>

            <script>
                let completedCount = 0;

                // Load today's practice
                fetch('/practices/daily')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('practice-content').innerHTML = 
                            `<h3>${data.practice}</h3>
                             <p>Day ${data.day_of_year} of your healing journey</p>`;
                        document.getElementById('practice-content').className = 'practice-card';
                    })
                    .catch(error => {
                        document.getElementById('practice-content').innerHTML = 
                            'Unable to load practice. Please refresh.';
                    });

                function startPractice() {
                    document.getElementById('practice-status').innerHTML = 
                        '<p class="loading">🕊️ Practice started... Take deep breaths</p>';
                }

                function completePractice() {
                    completedCount++;
                    document.getElementById('completed-count').textContent = completedCount;
                    document.getElementById('practice-status').innerHTML = 
                        '<p class="completed">✅ Practice completed! Well done!</p>';
                    
                    // Show celebration after completion
                    setTimeout(() => {
                        alert('🎉 Beautiful! Your healing practice is complete. Continue your journey tomorrow!');
                    }, 500);
                }

                function viewAllPractices() {
                    const container = document.getElementById('all-practices');
                    if (container.style.display === 'none') {
                        fetch('/practices/all')
                            .then(response => response.json())
                            .then(practices => {
                                let html = '<h3>All Healing Practices</h3>';
                                practices.forEach(practice => {
                                    html += `<div class="practice-card">
                                        <h4>${practice.name}</h4>
                                        <p>${practice.description}</p>
                                        <small>Duration: ${practice.duration} minutes</small>
                                    </div>`;
                                });
                                container.innerHTML = html;
                                container.style.display = 'block';
                            });
                    } else {
                        container.style.display = 'none';
                    }
                }
            </script>
        </body>
    </html>
    '''

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "benkhawiya-healing-platform",
        "domain": "sacredtreeofthephoenix.org"
    }

@app.get("/practices/daily")
async def daily_practice():
    day_of_year = datetime.now().timetuple().tm_yday
    practice_data = HEALING_PRACTICES[day_of_year % len(HEALING_PRACTICES)]
    
    return {
        "practice": f"{practice_data['name']}: {practice_data['description']}",
        "day_of_year": day_of_year,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "practice_data": practice_data
    }

@app.get("/practices/all")
async def all_practices():
    return HEALING_PRACTICES

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
