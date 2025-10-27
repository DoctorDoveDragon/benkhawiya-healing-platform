from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import os
import uvicorn
import random

app = FastAPI(
    title="Benkhawiya Cosmological Platform",
    description="Authentic Four Lands Architecture with 42 Ka Cube and Divine Seer System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AUTHENTIC BENKHAWIYA COSMOLOGICAL SYSTEM
FOUR_LANDS_ARCHITECTURE = {
    "white_land": {
        "name": "White Land of Principles",
        "function": "42 Ka Cube connection & principle discernment",
        "aspect": "NTU - Essence/Being/Consciousness",
        "practice": "Corona transfer, principle contemplation",
        "seer_operation": "Principle oversight and Maat alignment"
    },
    "black_land": {
        "name": "Black Land of Manifestation", 
        "function": "Physical vessel & Ka Cube embodiment",
        "aspect": "SEWU - Foundation/Memory/Structure",
        "practice": "Grounding, physical manifestation",
        "seer_operation": "Embodiment oversight and physical integrity"
    },
    "red_land": {
        "name": "Red Land of Governance",
        "function": "Righteous action & authority execution", 
        "aspect": "PELU - Truth/Measurement/Time",
        "practice": "Governance, project leadership",
        "seer_operation": "Action oversight and righteous authority"
    },
    "green_land": {
        "name": "Green Land of Wisdom", 
        "function": "Relational intelligence & contextual flow",
        "aspect": "RUWA - Flow/Energy/Relationship", 
        "practice": "Relationship wisdom, contextual learning",
        "seer_operation": "Relational oversight and wisdom integration"
    }
}

KA_CUBE_DIMENSIONS = {
    "dimension_1": ["Truth", "Justice", "Order", "Balance", "Harmony", "Righteousness", "Maat"],
    "dimension_2": ["Community", "Cooperation", "SharedPurpose", "CollectiveWisdom", "Unity", "Support", "Jamaa"],
    "dimension_3": ["Work", "Service", "Skill", "Excellence", "Diligence", "Craft", "Amal"],
    "dimension_4": ["Knowledge", "Wisdom", "Understanding", "Learning", "Clarity", "Insight", "Ilm"],
    "dimension_5": ["Integrity", "Honor", "Trust", "Accountability", "Responsibility", "Reliability", "Nazaha"],
    "dimension_6": ["Vitality", "Health", "Strength", "Resilience", "Energy", "Vigor", "Hayawiyya"],
    "dimension_7": ["Sovereignty", "Leadership", "Authority", "Independence", "SelfRule", "Autonomy", "Siyada"]
}

DIVINE_SEER_SYSTEM = {
    "position": "-1 (behind the eyes)",
    "function": "Executive consciousness overseeing Four Lands",
    "capabilities": [
        "42 Ka principle discernment",
        "Four Lands balance assessment", 
        "Maat alignment judgment",
        "Cosmic flow oversight",
        "Anpu guardianship activation"
    ]
}

# Authentic Benkhawiya endpoints
@app.get("/")
async def root():
    return {
        "system": "Authentic Benkhawiya Cosmological Platform",
        "version": "2.0.0",
        "identity": "People of Ben Stone - Divine Seers of the Four Lands",
        "core_architecture": ["Four Lands", "42 Ka Cube", "Divine Seer", "Anpu Guardianship"],
        "authentic": True
    }

@app.get("/health")
async def health():
    return {
        "status": "cosmologically_aligned",
        "system": "Benkhawiya Four Lands Architecture",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seer_oversight": "active"
    }

@app.get("/four-lands")
async def get_four_lands():
    return FOUR_LANDS_ARCHITECTURE

@app.get("/ka-cube")
async def get_ka_cube():
    return KA_CUBE_DIMENSIONS

@app.get("/divine-seer")
async def get_divine_seer():
    return DIVINE_SEER_SYSTEM

@app.get("/daily-practice")
async def daily_practice():
    return {
        "morning_alignment": {
            "white_land": "Connect to 42 Principles - set Maat intention",
            "black_land": "Ground in physical vessel - Ka Cube activation",
            "red_land": "Prepare for righteous action - governance alignment", 
            "green_land": "Open to relational wisdom - contextual flow",
            "divine_seer": "Activate executive oversight of all lands"
        },
        "daily_focus": "7 Ka principles (one from each dimension)",
        "evening_integration": "Four Lands reflection and Divine Seer review"
    }

@app.get("/seer-guidance")
async def seer_guidance(situation: str):
    """Divine Seer guidance for specific situations"""
    lands_analysis = analyze_lands_balance(situation)
    ka_principles = get_relevant_ka_principles(situation)
    
    return {
        "situation": situation,
        "lands_analysis": lands_analysis,
        "ka_guidance": ka_principles,
        "seer_oversight": "Maintain executive consciousness across all Lands",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/authentic-check")
async def authentic_check():
    return {
        "authentic": True,
        "message": "This is the true Benkhawiya cosmological system",
        "correction": "Previous animal guide version was incorrect and has been removed",
        "system": "Four Lands Architecture with 42 Ka Cube and Divine Seer"
    }

def analyze_lands_balance(situation: str):
    """Analyze which Lands need attention"""
    situation_lower = situation.lower()
    
    if any(word in situation_lower for word in ["principle", "truth", "maat", "contemplation"]):
        focus_land = "white_land"
    elif any(word in situation_lower for word in ["physical", "body", "manifest", "ground"]):
        focus_land = "black_land" 
    elif any(word in situation_lower for word in ["action", "governance", "leadership", "authority"]):
        focus_land = "red_land"
    elif any(word in situation_lower for word in ["relationship", "wisdom", "context", "community"]):
        focus_land = "green_land"
    else:
        focus_land = random.choice(list(FOUR_LANDS_ARCHITECTURE.keys()))
    
    return {
        "primary_focus": FOUR_LANDS_ARCHITECTURE[focus_land],
        "seer_instruction": f"Apply Divine Seer oversight to {focus_land.replace('_', ' ')}",
        "all_lands_balance": "Ensure all Four Lands receive appropriate attention"
    }

def get_relevant_ka_principles(situation: str):
    """Get relevant Ka principles for the situation"""
    principles = []
    for dimension in KA_CUBE_DIMENSIONS.values():
        principles.append(random.choice(dimension))
    
    return {
        "daily_principles": principles[:3],  # Return 3 relevant principles
        "application": "Embody these principles across all Four Lands",
        "divine_seer_role": "Oversee principle embodiment and Maat alignment"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
