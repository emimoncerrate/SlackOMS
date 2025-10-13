#!/bin/bash
# Quick start script for OMS API

echo "🚀 Starting OMS API..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating from template..."
    cp .env.template .env
    echo "Please edit .env with your configuration before running."
    exit 1
fi

# Initialize database
echo "🗄️  Initializing database..."
python -c "from app.database import init_db; init_db()"

# Start server
echo "✅ Starting server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

