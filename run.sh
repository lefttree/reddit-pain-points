#!/bin/bash
# Quick start script - runs both backend and frontend

set -e
cd "$(dirname "$0")"

echo "🎯 Reddit Pain Point Discovery Tool"
echo "===================================="

# Check .env
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your API credentials, then re-run."
    exit 1
fi

# Activate venv
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start backend
echo "🚀 Starting backend API server..."
cd backend
python cli.py serve --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "🎨 Starting frontend dev server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Services running:"
echo "   Backend API:  http://localhost:8000"
echo "   Frontend UI:  http://localhost:3000"
echo "   API Docs:     http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
