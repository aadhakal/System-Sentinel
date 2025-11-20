#!/bin/bash

echo "🚀 Starting System Sentinel Platform..."
echo ""

# Check if Docker is running
if docker ps &> /dev/null; then
    echo "✅ Docker is running"
else
    echo "⚠️  Docker is NOT running"
    echo ""
    echo "To enable REAL container automation:"
    echo "1. Open Docker Desktop app"
    echo "2. Wait for Docker to start"
    echo "3. Run this script again"
    echo ""
    echo "📝 The app will work in SIMULATION mode without Docker"
    echo ""
fi

# Check for existing containers from previous runs
EXISTING=$(docker ps -a --filter "name=web_server\|database_server\|monitoring_server" --format "{{.Names}}" 2>/dev/null | wc -l)
if [ "$EXISTING" -gt 0 ]; then
    echo ""
    echo "🔍 Found $EXISTING containers from previous runs"
    read -p "Do you want to clean them up? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rm -f $(docker ps -a --filter "name=web_server\|database_server\|monitoring_server" --format "{{.Names}}") 2>/dev/null
        echo "✅ Cleaned up old containers"
    fi
fi

echo ""
echo "🌐 Starting Flask application..."
echo "📊 Dashboard will be available at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python app.py
