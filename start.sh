#!/bin/bash

# Stock Screener Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting Stock Screener Application..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "  ✓ Backend server stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "  ✓ Frontend server stopped"
    fi
    exit 0
}

trap cleanup EXIT INT TERM

# Start Backend Server
echo "📡 Starting Flask backend server (port 5001)..."
cd "$SCRIPT_DIR/backend/api"
FLASK_ENV=development python app.py > "$SCRIPT_DIR/logs/backend-console.log" 2>&1 &
BACKEND_PID=$!
echo "  ✓ Backend PID: $BACKEND_PID"
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "  ✗ Backend failed to start. Check logs/backend-console.log"
    exit 1
fi

# Start Frontend Server
echo "⚛️  Starting React frontend server (port 3001)..."
cd "$SCRIPT_DIR/frontend"
PORT=3001 BROWSER=none npm start > "$SCRIPT_DIR/logs/frontend-console.log" 2>&1 &
FRONTEND_PID=$!
echo "  ✓ Frontend PID: $FRONTEND_PID"
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "  ✗ Frontend failed to start. Check logs/frontend-console.log"
    exit 1
fi

echo ""
echo "✅ Stock Screener is running!"
echo ""
echo "📊 Application URLs:"
echo "   Frontend: http://localhost:3001"
echo "   Backend API: http://localhost:5001/api"
echo ""
echo "📝 Logs:"
echo "   Backend: $SCRIPT_DIR/logs/backend-console.log"
echo "   Frontend: $SCRIPT_DIR/logs/frontend-console.log"
echo ""
echo "Press Ctrl+C to stop all servers..."
echo ""

# Wait for user interrupt
wait
