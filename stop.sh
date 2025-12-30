#!/bin/bash

# Stock Screener Stop Script
# This script stops both backend and frontend servers

echo "🛑 Stopping Stock Screener Application..."
echo ""

# Function to kill process by port
kill_by_port() {
    local port=$1
    local name=$2

    echo "Checking for $name on port $port..."

    # Find process using the port
    PID=$(lsof -ti:$port)

    if [ -z "$PID" ]; then
        echo "  ℹ️  No $name process found on port $port"
    else
        echo "  🔍 Found $name process (PID: $PID)"
        kill -15 $PID 2>/dev/null

        # Wait up to 5 seconds for graceful shutdown
        for i in {1..5}; do
            if ! kill -0 $PID 2>/dev/null; then
                echo "  ✓ $name stopped gracefully"
                return 0
            fi
            sleep 1
        done

        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            echo "  ⚠️  Forcing $name to stop..."
            kill -9 $PID 2>/dev/null
            echo "  ✓ $name force stopped"
        fi
    fi
}

# Stop Backend (Flask on port 5001)
kill_by_port 5001 "Backend (Flask)"

# Stop Frontend (React on port 3001)
kill_by_port 3001 "Frontend (React)"

# Also check default React port 3000 in case it's there
kill_by_port 3000 "Frontend (React - alternate)"

# Kill any remaining python processes running app.py
echo ""
echo "Checking for any remaining app.py processes..."
REMAINING_PIDS=$(pgrep -f "python.*app.py")
if [ -n "$REMAINING_PIDS" ]; then
    echo "  🔍 Found remaining processes: $REMAINING_PIDS"
    echo "$REMAINING_PIDS" | xargs kill -15 2>/dev/null
    sleep 1
    echo "  ✓ Cleaned up remaining processes"
else
    echo "  ℹ️  No remaining app.py processes found"
fi

# Kill any remaining npm/node processes for the frontend
echo ""
echo "Checking for any remaining React processes..."
REMAINING_NODE=$(pgrep -f "react-scripts start")
if [ -n "$REMAINING_NODE" ]; then
    echo "  🔍 Found remaining Node processes: $REMAINING_NODE"
    echo "$REMAINING_NODE" | xargs kill -15 2>/dev/null
    sleep 1
    echo "  ✓ Cleaned up remaining Node processes"
else
    echo "  ℹ️  No remaining React processes found"
fi

echo ""
echo "✅ Stock Screener stopped successfully!"
echo ""
echo "To start again, run: ./start.sh"
