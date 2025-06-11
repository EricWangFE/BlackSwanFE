#!/bin/bash

echo "Starting Black Swan Backend Development Server..."

# Export development environment variables
export ENV=development
export DATABASE_URL="postgresql://blackswan:password@localhost:5432/blackswan"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET_KEY="dev-secret-key-change-in-production"
export ALLOWED_ORIGINS="http://localhost:3000"

# Check if Redis is running
if ! command -v redis-cli &> /dev/null; then
    echo "Warning: Redis CLI not found. Make sure Redis is running."
else
    redis-cli ping > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Warning: Redis is not running. Starting Redis..."
        redis-server --daemonize yes
    fi
fi

# Start the application
echo "Starting FastAPI server on http://localhost:8000"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000