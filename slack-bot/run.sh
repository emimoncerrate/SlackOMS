#!/bin/bash
# Quick start script for Slack Bot

echo "🤖 Starting Slack Bot..."

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
    echo ""
    echo "Please edit .env with your configuration:"
    echo "  1. SLACK_BOT_TOKEN (from Slack App)"
    echo "  2. SLACK_SIGNING_SECRET (from Slack App)"
    echo "  3. OMS_API_URL (your OMS API URL)"
    echo "  4. OMS_API_KEY (your OMS API key)"
    echo ""
    exit 1
fi

# Start bot
echo "✅ Starting Slack Bot..."
python main.py

