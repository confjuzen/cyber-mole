#!/bin/bash

# Create and activate Python venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install Python packages for backend
pip install -r backend/requirements.txt

# Install Node.js packages for frontend
cd frontend && npm install

# Build Java service
cd ../smile-service && mvn package

# Launch services in background
# Backend
cd ../backend && python app/app.py &
BACKEND_PID=$!

# Frontend
cd ../frontend && npm run dev &
FRONTEND_PID=$!

# Java service
cd ../smile-service && java -jar target/smile-service-1.0.0.jar &
JAVA_PID=$!

# Wait a bit for services to start
sleep 5

# Open browser to frontend
xdg-open http://localhost:3004 &

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID $JAVA_PID
