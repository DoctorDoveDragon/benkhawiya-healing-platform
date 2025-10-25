#!/bin/bash

echo "🚀 DEPLOYING PRODUCTION CODE"

cd ~/benkhawiya-healing-production/backend

echo "📤 Force pushing to GitHub..."
git add .
git commit -m "Production deployment: FastAPI single-file app" 2>/dev/null || echo "No new changes"
git push -f origin main

echo "🔗 Setting up Railway..."
railway login
railway init
railway add postgresql
railway variables set SECRET_KEY="benkhawiya-secure-production-key-2024-32-chars"
railway variables set ENVIRONMENT="production"

echo "🎯 Deploying to Railway..."
railway deploy

echo "✅ DEPLOYMENT INITIATED!"
echo "📋 Check deployment progress with: railway logs"
