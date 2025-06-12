# Testing Replit Deployment

This guide helps you test the Replit deployment before pushing to GitHub.

## Quick Test

Run the local test script:
```bash
./test-replit-local.sh
```

This script will:
1. Check prerequisites (Python, Node.js, Redis)
2. Test backend setup and imports
3. Test frontend build
4. Validate Replit configuration files
5. Simulate the Replit startup process

## GitHub Actions Testing

The `replit-deployment` branch includes automated tests that run on every push:

- **Backend Tests**: Validates Python dependencies and API startup
- **Frontend Tests**: Ensures the app builds with Replit URLs
- **Configuration Tests**: Checks `.replit`, `replit.nix`, and `run.sh`
- **Environment Simulation**: Tests with Replit-like environment variables

View test results at: https://github.com/EricWangFE/BlackSwanFE/actions

## Manual Testing Steps

### 1. Test Backend Locally
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set test environment variables
export JWT_SECRET_KEY="test-secret-key-32-characters-long"
export DATABASE_URL="sqlite:///./test.db"
export REDIS_URL="redis://localhost:6379"

# Start backend
python -m uvicorn main:app --reload

# In another terminal, test the API
curl http://localhost:8000/health
```

### 2. Test Frontend Locally
```bash
cd frontend
npm install

# Set Replit-style environment variables
export NEXT_PUBLIC_API_URL="http://localhost:8000"
export NEXT_PUBLIC_SOCKET_URL="ws://localhost:8000"
export NEXTAUTH_SECRET="test-secret-key-32-characters-long"

# Build and run
npm run build
npm start

# Visit http://localhost:3000
```

### 3. Validate Replit Files

Check `.replit` configuration:
```bash
# Should contain run command and port configuration
cat .replit
```

Check `replit.nix` dependencies:
```bash
# Should list Python, Node.js, and other system dependencies
cat replit.nix
```

Test `run.sh` script:
```bash
# Check syntax
bash -n run.sh

# View what it does (don't run it locally)
cat run.sh
```

## Common Issues and Solutions

### Issue: Dependencies fail to install
**Solution**: Check that `requirements.txt` uses compatible versions (especially `redis==4.6.0` for Celery)

### Issue: Frontend build fails
**Solution**: Ensure `package-lock.json` is in sync with `package.json` (run `npm install` to regenerate)

### Issue: WebSocket connection errors
**Solution**: Verify the URL construction in `frontend/src/lib/websocket/socket.ts` handles Replit environment

### Issue: API keys not working
**Solution**: In Replit, use the Secrets tab (🔒) to add environment variables, not `.env` files

## Pre-Deployment Checklist

- [ ] Run `./test-replit-local.sh` - all tests pass
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] `.replit` file is valid TOML
- [ ] `run.sh` has executable permissions
- [ ] No hardcoded localhost URLs
- [ ] Environment variables use Replit patterns

## Deployment Steps

1. Push to GitHub:
   ```bash
   git add .
   git commit -m "Update Replit deployment"
   git push origin replit-deployment
   ```

2. Import to Replit:
   - Go to https://replit.com/github/EricWangFE/BlackSwanFE
   - Select the `replit-deployment` branch
   - Click Import

3. Configure Secrets in Replit:
   - Add all required API keys
   - Use the Secrets tab, not `.env` files

4. Run the app:
   - Click the green Run button
   - Wait for dependencies to install (first run takes 2-3 minutes)
   - Access via the provided URL

## Monitoring

After deployment, check:
- Console output for any errors
- `/health` endpoint responds
- Frontend loads without console errors
- WebSocket connects successfully