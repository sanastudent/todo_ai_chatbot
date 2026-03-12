#!/bin/bash

# Function to check backend health
check_backend_health() {
    local max_retries=30
    local retry_interval=2
    local attempt=0

    echo "🔍 Checking backend health..."

    while [ $attempt -lt $max_retries ]; do
        if curl -f -s -o /dev/null http://localhost:8000/health; then
            echo "✅ Backend health check passed!"
            return 0
        else
            echo "⚠️  Backend not reachable yet (Attempt $((attempt + 1))/$max_retries)"
            sleep $retry_interval
            attempt=$((attempt + 1))
        fi
    done

    echo "💥 Backend health check failed after maximum retries"
    return 1
}

# Start backend server in background
echo "🚀 Starting backend server on port 8000..."
cd backend && python run_server.py &
BACKEND_PID=$!

# Wait for backend to be ready using health check
if check_backend_health; then
    echo "🎉 Backend is healthy and ready!"
    echo "🚀 Starting frontend server on port 5174..."

    # Start frontend server
    cd ../frontend && npm run dev
else
    echo "💥 Failed to start: Backend did not become healthy within timeout period."
    echo "❌ Terminating backend process..."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Clean up when script exits
trap 'kill $(jobs -p) 2>/dev/null' EXIT