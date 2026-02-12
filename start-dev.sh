#!/bin/bash

# Stock Screener Development Startup Script
# This script starts both servers and shows their output in the terminal

echo "🚀 Starting Stock Screener in Development Mode..."
echo ""
echo "Starting backend and frontend servers..."
echo "Backend will run on: http://localhost:5001"
echo "Frontend will run on: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "================================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    jobs -p | xargs -r kill 2>/dev/null
    exit 0
}

trap cleanup EXIT INT TERM

# Start Backend Server in background
cd "$SCRIPT_DIR/backend/api"
python app.py &

# Start Frontend Server in background
cd "$SCRIPT_DIR/frontend"
PORT=3001 BROWSER=none npm start &

# Wait for all background jobs
wait
