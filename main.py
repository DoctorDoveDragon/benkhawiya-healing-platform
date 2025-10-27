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
    description="Ancestral spiritual healing through the Four Lands",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CULTURAL FOUNDATION: THE FOUR LANDS
FOUR_LANDS = {
    "eastern_land": {
        "name": "Land of New Beginnings",
        "element": "Air",
        "direction": "East", 
        "teaching": "Wisdom and Clarity",
        "animal": "Eagle",
        "color": "Gold",
        "practice": "Morning meditation for clear vision"
    },
    "southern_land": {
        "name": "Land of Growth", 
        "element": "Fire",
        "direction": "South",
        "teaching": "Passion and Transformation",
        "animal": "Lion",
        "color": "Red",
        "practice": "Energy work for personal power"
    },
    "western_land": {
        "name": "Land of Introspection",
        "element": "Water", 
        "direction": "West",
        "teaching": "Emotional Healing",
        "animal": "Bear",
        "color": "Blue",
        "practice": "Evening reflection for emotional balance"
    },
    "northern_land": {
        "name": "Land of Ancestral Wisdom",
        "element": "Earth",
        "direction": "North",
        "teaching": "Foundation and Tradition",
        "animal": "Buffalo",
        "color": "Green", 
        "practice": "Ancestral connection practices"
    }
}

HEALING_PRACTICES = [
    {
        "name": "Eastern Gate: Eagle Vision Meditation",
        "land": "eastern_land",
        "description": "Connect with the Eastern Land's wisdom through elevated perspective",
        "duration": 15,
        "steps": [
            "Face East towards new beginnings",
            "Visualize golden light of dawn", 
            "Call upon Eagle's far-seeing vision",
            "Receive clarity for your path ahead"
        ],
        "cultural_context": "The Eastern Land teaches us to see beyond immediate circumstances to the larger journey"
    },
    {
        "name": "Southern Fire: Lion Heart Activation",
        "land": "southern_land", 
        "description": "Ignite your inner fire with Southern Land's transformative energy",
        "duration": 20,
        "steps": [
            "Face South with open heart",
            "Feel the red fire of passion",
            "Channel Lion's courage and strength", 
            "Transform challenges into power"
        ],
        "cultural_context": "The Southern Land reminds us that our greatest trials forge our strongest spirit"
    },
    {
        "name": "Western Waters: Bear Heart Healing",
        "land": "western_land",
        "description": "Journey inward with Western Land's healing waters",
        "duration": 25,
        "steps": [
            "Face West at sunset",
            "Welcome blue healing waters",
            "Enter Bear's cave of introspection",
            "Release emotional burdens to the waters"
        ],
        "cultural_context": "The Western Land teaches that true strength comes from emotional honesty and healing"
    },
    {
        "name": "Northern Roots: Buffalo Ancestral Connection", 
        "land": "northern_land",
        "description": "Ground in ancestral wisdom through Northern Land's stability",
        "duration": 30,
        "steps": [
            "Face North under night sky",
            "Feel green earth energy rising",
            "Connect with Buffalo's enduring spirit",
            "Receive ancestral guidance and blessings"
        ],
        "cultural_context": "The Northern Land reminds us we walk on the shoulders of ancestors who guide our path"
    }
]

@app.get("/", response_class=HTMLResponse)
async def cultural_homepage():
    return '''
    <html>
        <head>
            <title>Benkhawiya Healing Platform</title>
            <style>
                body { 
                    font-family: 'Georgia', serif;
                    margin: 0;
                    padding: 20px;
                    background: #0a2f1c;
                    color: #e8d8b8;
                    min-height: 100vh;
                }
                .container {
                    max-width: 900px;
                    margin: 0 auto;
                    background: rgba(20, 60, 40, 0.8);
                    padding: 30px;
                    border-radius: 15px;
                    border: 2px solid #8b7355;
                }
                h1 { 
                    color: #d4af37;
                    text-align: center;
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px #000;
                }
                .subtitle {
                    text-align: center;
                    color: #b8860b;
                    font-style: italic;
                    margin-bottom: 30px;
                }
                .lands-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin: 30px 0;
                }
                .land-card {
                    background: rgba(139, 115, 85, 0.3);
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #8b7355;
                    text-align: center;
                }
                .land-card.east { border-top: 5px solid #ffd700; }
                .land-card.south { border-top: 5px solid #dc143c; }
                .land-card.west { border-top: 5px solid #1e90ff; }
                .land-card.north { border-top: 5px solid #228b22; }
                
                .practice-card {
                    background: rgba(212, 175, 55, 0.1);
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 10px;
                    border-left: 5px solid #d4af37;
                }
                .btn {
                    background: #8b7355;
                    color: #e8d8b8;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 10px 5px;
                    font-family: 'Georgia', serif;
                    border: 1px solid #d4af37;
                }
                .btn:hover {
                    background: #d4af37;
                    color: #0a2f1c;
                }
                .cultural-context {
                    font-style: italic;
                    color: #b8860b;
                    border-top: 1px solid #8b7355;
                    padding-top: 10px;
                    margin-top: 15px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌿 Benkhawiya Healing Platform</h1>
                <div class="subtitle">Walking the Sacred Path Through the Four Lands</div>
                
                <div class="lands-grid">
                    <div class="land-card east">
                        <h3>🦅 Eastern Land</h3>
                        <p>Land of New Beginnings</p>
                        <p><em>Element: Air • Teaching: Wisdom</em></p>
                    </div>
                    <div class="land-card south">
                        <h3>🦁 Southern Land</h3>
                        <p>Land of Growth</p>
                        <p><em>Element: Fire • Teaching: Transformation</em></p>
                    </div>
                    <div class="land-card west">
                        <h3>🐻 Western Land</h3>
                        <p>Land of Introspection</p>
                        <p><em>Element: Water • Teaching: Healing</em></p>
                    </div>
                    <div class="land-card north">
                        <h3>🐃 Northern Land</h3>
                        <p>Land of Ancestral Wisdom</p>
                        <p><em>Element: Earth • Teaching: Foundation</em></p>
                    </div>
                </div>

                <div id="daily-practice">
                    <h2>Today's Journey Through the Lands</h2>
                    <div id="practice-content">
                        <div class="practice-card">
                            <h3 id="practice-name">Loading your sacred practice...</h3>
                            <p id="practice-desc"></p>
                            <div id="practice-steps"></div>
                            <div id="cultural-context" class="cultural-context"></div>
                        </div>
                    </div>
                    <button class="btn" onclick="beginJourney()">Begin Sacred Journey</button>
                    <button class="btn" onclick="completeJourney()">Complete Journey</button>
                    <div id="journey-status"></div>
                </div>

                <div style="text-align: center; margin-top: 30px;">
                    <p><em>"We walk the four lands not as separate places, but as one continuous sacred circle of being."</em></p>
                </div>
            </div>

            <script>
                // Load today's culturally-grounded practice
                fetch('/practices/daily')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('practice-name').textContent = data.practice_data.name;
                        document.getElementById('practice-desc').textContent = data.practice_data.description;
                        
                        let stepsHtml = '<h4>Journey Steps:</h4><ol>';
                        data.practice_data.steps.forEach(step => {
                            stepsHtml += `<li>${step}</li>`;
                        });
                        stepsHtml += '</ol>';
                        document.getElementById('practice-steps').innerHTML = stepsHtml;
                        
                        document.getElementById('cultural-context').textContent = 
                            data.practice_data.cultural_context;
                    });

                function beginJourney() {
                    const landName = document.getElementById('practice-name').textContent.split(':')[0];
                    document.getElementById('journey-status').innerHTML = 
                        `<p style="color: #d4af37;">🕊️ Beginning your journey through ${landName}... May the ancestors guide your steps.</p>`;
                }

                function completeJourney() {
                    document.getElementById('journey-status').innerHTML = 
                        `<p style="color: #228b22;">✅ Journey completed! The lands have received your prayers. 
                        <br><em>"With each completed journey, we strengthen the circle for all who follow."</em></p>`;
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
        "domain": "sacredtreeofthephoenix.org",
        "cultural_foundation": "Four Lands Tradition"
    }

@app.get("/practices/daily")
async def daily_practice():
    day_of_year = datetime.now().timetuple().tm_yday
    practice_data = HEALING_PRACTICES[day_of_year % len(HEALING_PRACTICES)]
    land_info = FOUR_LANDS[practice_data["land"]]
    
    return {
        "practice": f"{practice_data['name']} - {land_info['name']}",
        "day_of_year": day_of_year,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "practice_data": practice_data,
        "land_info": land_info
    }

@app.get("/practices/all")
async def all_practices():
    return HEALING_PRACTICES

@app.get("/four-lands")
async def four_lands():
    return FOUR_LANDS

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
