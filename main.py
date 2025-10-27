from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import os
import uvicorn
import random

app = FastAPI(
    title="Benkhawiya Healing Platform",
    description="Sacred Four Lands Ancestral Healing System",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sacred Four Lands Tradition
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

# Spiritual Guidance System
SPIRITUAL_GUIDES = {
    "white_land": {
        "guide": "White Buffalo Ancestor",
        "wisdom": [
            "The White Land holds pure consciousness that precedes all manifestation",
            "Your ancestral memories flow through you like a sacred river",
            "Memory is re-membering - putting the pieces of your soul back together",
            "Ancestral recall is reaching inward to the eternal now"
        ],
        "chants": ["Ntu dumo, sewu karibu", "Ntu se sewu wapi?"]
    },
    "black_land": {
        "guide": "Quantum Panther of the Void",
        "wisdom": [
            "The Black Land is the quantum field of infinite possibilities",
            "The void is pregnant with every possible creation",
            "True potential is what the universe can do through you",
            "In the void, there is no separation between what is and what could be"
        ],
        "chants": ["Sewu wapi, ntu tayari", "Pelu ya wewe ni nini?"]
    },
    "red_land": {
        "guide": "Red Hawk of Manifestation",
        "wisdom": [
            "The Red Land transforms potential into reality through creative fire",
            "Your life force is the cosmic creative impulse made personal",
            "Manifestation is allowing what wants to happen through you",
            "The Red Hawk sees patterns wanting to manifest through your actions"
        ],
        "chants": ["Moyo wa moto, uwezo wa kuumba", "Pelu inatoka nje"]
    },
    "green_land": {
        "guide": "Green Serpent of Regeneration", 
        "wisdom": [
            "The Green Land connects all beings in the great web of relationship",
            "Healing flows through you to the collective and back again",
            "Regeneration is remembering what is already whole",
            "Your breath is the same breath that moves through forests and oceans"
        ],
        "chants": ["Mimea inmea, uhai unazidi", "Moyo mmoja, roho nyingi"]
    }
}

def analyze_spiritual_intent(message: str):
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["ancestor", "memory", "white", "spirit", "past"]):
        land = "white_land"
    elif any(word in message_lower for word in ["void", "potential", "black", "possibility", "future"]):
        land = "black_land"
    elif any(word in message_lower for word in ["manifest", "red", "fire", "create", "action"]):
        land = "red_land"
    elif any(word in message_lower for word in ["green", "heal", "grow", "connect", "earth"]):
        land = "green_land"
    else:
        land = random.choice(list(FOUR_LANDS.keys()))
    
    return {
        "primary_land": land,
        "confidence": 0.8,
        "emotional_tone": "guidance"
    }

def generate_spiritual_response(message: str):
    intent = analyze_spiritual_intent(message)
    land = intent["primary_land"]
    guide = SPIRITUAL_GUIDES[land]
    
    wisdom = random.choice(guide["wisdom"])
    chant = random.choice(guide["chants"])
    
    return {
        "guide": guide["guide"],
        "message": wisdom,
        "chant": chant,
        "land": land,
        "land_info": FOUR_LANDS[land],
        "blessing": FOUR_LANDS[land]["blessing"],
        "user_message": message
    }

# CHAT ENDPOINTS - These are the missing ones!
@app.post("/chat/send")
async def chat_send(message: str):
    """Send a message to spiritual guides"""
    response = generate_spiritual_response(message)
    return {
        **response,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "guided"
    }

@app.get("/chat/analysis")
async def chat_analysis(message: str):
    """Analyze spiritual intent of a message"""
    intent = analyze_spiritual_intent(message)
    return {
        "analysis": intent,
        "user_message": message,
        "suggested_land": FOUR_LANDS[intent["primary_land"]],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/chat/guides")
async def get_guides():
    """Get all spiritual guides"""
    return SPIRITUAL_GUIDES

# ORIGINAL ENDPOINTS (keep these)
@app.get("/")
async def root():
    return {
        "message": "Benkhawiya Healing Platform", 
        "version": "3.0.0", 
        "status": "active",
        "chat_available": True,
        "url": "https://sacredtreeofthephoenix.org"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "benkhawiya-healing-platform",
        "cosmology": "Four Lands Tradition",
        "lands": list(FOUR_LANDS.keys()),
        "chat": "available"
    }

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

@app.post("/auth/register")
async def register(email: str, spiritual_name: str = None):
    return {
        "message": "Welcome to the Benkhawiya journey",
        "email": email,
        "spiritual_name": spiritual_name,
        "status": "registered_in_memory"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
