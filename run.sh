#!/bin/bash

echo "🚀 Starting Black Swan Event Detection System on Replit..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create necessary directories
mkdir -p logs

# Install Python dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
cd backend
pip install -r requirements.txt

# Initialize databases
echo -e "${BLUE}Starting Redis...${NC}"
redis-server --daemonize yes --port 6379

# Start PostgreSQL (Replit provides it as a service)
if [ -z "$DATABASE_URL" ]; then
    echo -e "${BLUE}Setting up local PostgreSQL...${NC}"
    export DATABASE_URL="postgresql://replit:replit@localhost/blackswan"
fi

# Start the backend
echo -e "${GREEN}Starting Backend API...${NC}"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Install frontend dependencies
echo -e "${BLUE}Installing Frontend dependencies...${NC}"
cd ../frontend
npm install

# Build frontend
echo -e "${BLUE}Building Frontend...${NC}"
npm run build

# Start frontend
echo -e "${GREEN}Starting Frontend...${NC}"
npm start &
FRONTEND_PID=$!

echo -e "${GREEN}✅ Black Swan System is running!${NC}"
echo "Backend API: https://$REPL_SLUG.$REPL_OWNER.repl.co:8000"
echo "Frontend: https://$REPL_SLUG.$REPL_OWNER.repl.co"
echo "API Docs: https://$REPL_SLUG.$REPL_OWNER.repl.co:8000/docs"

# Keep the script running
wait $BACKEND_PID $FRONTEND_PID