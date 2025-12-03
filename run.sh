#!/bin/bash

echo "🏔️ SmartStyle AI - Starting Application..."
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys before continuing."
    echo "Press Enter after adding your API keys..."
    read
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -q -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python3 -c "from app.database import init_db; init_db()" 2>/dev/null

# Seed data
echo "🌱 Seeding initial data..."
python3 seed_data.py

# Start server
echo "🚀 Starting SmartStyle AI server..."
echo "=========================================="
echo "✅ Application running at: http://localhost:8000"
echo "📧 Demo account: demo@smartstyle.ai / Demo123!"
echo "=========================================="
python3 app/main.py
