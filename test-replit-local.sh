#!/bin/bash

# Local testing script to simulate Replit environment
# This helps test the Replit deployment before pushing to GitHub

echo "🧪 Testing Replit deployment locally..."

# Set up environment variables to simulate Replit
export REPL_SLUG="test-blackswan"
export REPL_OWNER="local-test"
export DATABASE_URL="sqlite:///./test.db"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET_KEY="test-secret-key-32-characters-long"
export NEXTAUTH_SECRET="test-secret-key-32-characters-long"
export ANTHROPIC_API_KEY="dummy-anthropic-key"
export OPENAI_API_KEY="dummy-openai-key"
export PINECONE_API_KEY="dummy-pinecone-key"
export PINECONE_ENV="us-east-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
        exit 1
    fi
}

echo -e "\n${YELLOW}1. Checking prerequisites...${NC}"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
else
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"
else
    echo -e "${RED}✗ Node.js not found${NC}"
    exit 1
fi

# Check Redis (optional for local testing)
if command_exists redis-cli; then
    if redis-cli ping >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis is running${NC}"
    else
        echo -e "${YELLOW}⚠ Redis installed but not running (tests will use mock)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Redis not installed (tests will use mock)${NC}"
fi

echo -e "\n${YELLOW}2. Testing backend...${NC}"

# Create Python virtual environment
cd backend
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt >/dev/null 2>&1
print_status $? "Backend dependencies installed"

# Test backend imports
echo "Testing backend imports..."
python3 -c "
try:
    from main import app
    from config.settings import settings
    print('Backend imports successful')
    exit(0)
except Exception as e:
    print(f'Import error: {e}')
    exit(1)
" >/dev/null 2>&1
print_status $? "Backend imports work"

# Test backend startup
echo "Testing backend startup..."
timeout 10s python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 >/dev/null 2>&1 &
BACKEND_PID=$!
sleep 5

# Check if backend is running
if curl -f http://localhost:8001/health >/dev/null 2>&1; then
    print_status 0 "Backend starts and responds to health check"
    kill $BACKEND_PID 2>/dev/null
else
    kill $BACKEND_PID 2>/dev/null
    print_status 1 "Backend failed to start"
fi

deactivate
cd ..

echo -e "\n${YELLOW}3. Testing frontend...${NC}"

cd frontend

# Check package.json exists
if [ -f "package.json" ]; then
    print_status 0 "package.json found"
else
    print_status 1 "package.json not found"
fi

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm ci >/dev/null 2>&1
print_status $? "Frontend dependencies installed"

# Test frontend build
echo "Building frontend..."
export NEXT_PUBLIC_API_URL="https://$REPL_SLUG.$REPL_OWNER.repl.co:8000"
export NEXT_PUBLIC_SOCKET_URL="wss://$REPL_SLUG.$REPL_OWNER.repl.co:8000"
export NEXTAUTH_URL="https://$REPL_SLUG.$REPL_OWNER.repl.co"

npm run build >/dev/null 2>&1
print_status $? "Frontend builds successfully"

cd ..

echo -e "\n${YELLOW}4. Testing Replit-specific files...${NC}"

# Test run.sh
if [ -x "run.sh" ]; then
    bash -n run.sh 2>/dev/null
    print_status $? "run.sh has valid syntax"
else
    print_status 1 "run.sh is not executable"
fi

# Test .replit
if [ -f ".replit" ]; then
    python3 -c "
import toml
try:
    with open('.replit', 'r') as f:
        config = toml.load(f)
    print('.replit is valid TOML')
    exit(0)
except:
    exit(1)
" >/dev/null 2>&1
    print_status $? ".replit configuration is valid"
else
    print_status 1 ".replit file not found"
fi

# Test replit.nix
if [ -f "replit.nix" ]; then
    if grep -q "pkgs" replit.nix && grep -q "deps" replit.nix; then
        print_status 0 "replit.nix has required fields"
    else
        print_status 1 "replit.nix missing required fields"
    fi
else
    print_status 1 "replit.nix file not found"
fi

echo -e "\n${YELLOW}5. Simulating full Replit startup...${NC}"

# Test if run.sh would work
echo "Simulating run.sh execution..."
# Don't actually run it, just check if the commands would work
if command_exists pip && command_exists npm; then
    print_status 0 "Required commands for run.sh are available"
else
    print_status 1 "Missing required commands for run.sh"
fi

echo -e "\n${GREEN}✅ All tests passed! Your app should work on Replit.${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Commit and push to the replit-deployment branch"
echo "2. Import into Replit using: https://replit.com/github/EricWangFE/BlackSwanFE"
echo "3. Add your real API keys in Replit Secrets"
echo "4. Click Run!"

# Cleanup
if [ -n "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null
fi