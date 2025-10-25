#!/bin/bash

echo "🚀 DEPLOYING BENKHAWIYA HEALING PLATFORM"

# Check environment
echo "🔍 Environment check..."
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️ WARNING: DATABASE_URL not set"
else
    echo "✅ DATABASE_URL is set"
fi

if [ -z "$SECRET_KEY" ]; then
    echo "⚠️ WARNING: SECRET_KEY not set, using fallback"
else
    echo "✅ SECRET_KEY is set"
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git add .
git commit -m "Production deployment: single-file app with robust error handling"
git push origin main

echo "✅ Code pushed to GitHub"
echo "🎯 Now run: railway deploy"
