#!/bin/bash

echo "🚀 FIXING DEPLOYMENT..."

cd ~/benkhawiya-healing-production/backend

# Update railway.json
cat > railway.json << 'RAILWAY_EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1",
    "restartPolicyType": "ON_FAILURE",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 80
  }
}
RAILWAY_EOF

echo "📤 Deploying fix..."
git add .
git commit -m "Fix: Use uvicorn production server"
git push origin main
railway deploy

echo "✅ Fix deployed! Health check should now pass."
