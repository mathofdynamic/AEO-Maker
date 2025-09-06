#!/bin/bash

# LLM.txt Generator - Service Startup Script
# ==========================================
# This script starts all required services for the LLM.txt Generator

echo "🚀 Starting LLM.txt Generator Services..."
echo "=========================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "✅ Port $port is already in use"
        return 0
    else
        echo "❌ Port $port is free"
        return 1
    fi
}

# Start Sitemap Service
echo "📋 Starting Sitemap Service (port 5000)..."
if check_port 5000; then
    echo "   Sitemap Service already running"
else
    cd Sitemap_Service
    python3 sitemap_api.py &
    SITEMAP_PID=$!
    echo "   Sitemap Service started with PID: $SITEMAP_PID"
    cd ..
fi

# Start Scraper Service  
echo "🔍 Starting Scraper Service (port 8000)..."
if check_port 8000; then
    echo "   Scraper Service already running"
else
    cd Text_Scrapper_Service
    python3 scraper_api.py &
    SCRAPER_PID=$!
    echo "   Scraper Service started with PID: $SCRAPER_PID"
    cd ..
fi

# Start Screenshot Service
echo "📸 Starting Screenshot Service (port 5002)..."
if check_port 5002; then
    echo "   Screenshot Service already running"
else
    cd Screenshot_Service
    python3 screenshot_api.py &
    SCREENSHOT_PID=$!
    echo "   Screenshot Service started with PID: $SCREENSHOT_PID"
    cd ..
fi

# Wait a moment for services to start
echo "⏳ Waiting for services to initialize..."
sleep 3

# Check service health
echo "🔍 Checking service health..."
echo ""

# Check Sitemap Service
echo -n "Sitemap Service: "
if curl -s http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Not responding"
fi

# Check Scraper Service
echo -n "Scraper Service: "
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Not responding"
fi

# Check Screenshot Service
echo -n "Screenshot Service: "
if curl -s http://localhost:5002/health >/dev/null 2>&1; then
    echo "✅ Healthy"
else
    echo "❌ Not responding"
fi

echo ""
echo "🎯 All services started!"
echo "🌐 Main Application: http://localhost:5001"
echo ""
echo "📝 To stop all services, press Ctrl+C or run: pkill -f 'python3.*api.py'"
echo ""

# Keep script running to maintain services
echo "🔄 Services are running in the background..."
echo "   Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap 'echo ""; echo "🛑 Stopping all services..."; pkill -f "python3.*api.py"; echo "✅ All services stopped"; exit 0' INT

# Keep running
while true; do
    sleep 1
done
