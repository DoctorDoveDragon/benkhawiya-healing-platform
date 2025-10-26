#!/bin/bash

echo "🚀 FINAL DEPLOYMENT"

cd ~/benkhawiya-healing-production/backend

echo "🔗 Setting up Railway project..."
if railway link 2>/dev/null; then
    echo "✅ Project linked"
else
    echo "🆕 Creating new project..."
    railway init
fi

echo "🐘 Adding PostgreSQL..."
railway add postgresql

echo "⚙️ Setting environment variables..."
railway variables SECRET_KEY="benkhawiya-production-secure-key-2024-32-chars"
railway variables ENVIRONMENT="production"

echo "🎯 DEPLOYING..."
railway deploy

echo "✅ DEPLOYMENT COMPLETE!"
echo "🌐 Check your live app with: railway status"
echo "📋 View logs with: railway logs"
