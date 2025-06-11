# Black Swan Event Detection System

![CI](https://github.com/EricWangFE/BlackSwanFE/workflows/CI/badge.svg)
[![Railway](https://img.shields.io/badge/Deploy%20on-Railway-purple)](https://railway.app)
[![Vercel](https://img.shields.io/badge/Deploy%20on-Vercel-black)](https://vercel.com)

Real-time cryptocurrency black swan event detection using multi-agent LLMs.

## 🎯 What This App Does

**Black Swan** monitors crypto markets 24/7 and alerts you to potential catastrophic events BEFORE they fully unfold:

- 📊 **Real-time Monitoring**: Tracks news, social media, and market data
- 🤖 **AI Analysis**: Multiple LLMs analyze events for severity and impact
- 🚨 **Smart Alerts**: Get notified only when something significant happens
- 📈 **Risk Assessment**: Detailed analysis with confidence scores
- ⚡ **WebSocket Updates**: Live dashboard with instant updates

Perfect for traders, researchers, and anyone interested in crypto market risks.

## 🚀 Quick Deploy (5 minutes)

### Step 1: Deploy Backend to Railway

1. **Fork this repository** on GitHub
   - Click the "Fork" button at the top right
   - This creates your own copy of the code

2. **Create Railway Account:**
   - Go to [Railway.app](https://railway.app)
   - Sign up with GitHub (recommended) or email
   - Verify your account

3. **Deploy the Backend:**
   - Click **"Start a New Project"**
   - Select **"Deploy from GitHub repo"**
   - Choose your forked repository
   - Select the `/backend` directory when prompted
   - Click **"Deploy Now"**

4. **Add Required Databases:**
   - In your Railway project dashboard:
   - Click **"+ New"** → **"Database"** → **"Add PostgreSQL"**
   - Click **"+ New"** → **"Database"** → **"Add Redis"**
   - Wait for both to provision (∼30 seconds)
   - Railway automatically injects `DATABASE_URL` and `REDIS_URL`

5. **Add API Keys & Secrets:**
   - Click on your app service (not the databases)
   - Go to **"Variables"** tab
   - Click **"Raw Editor"** and paste this template:
   ```
   ANTHROPIC_API_KEY=your-anthropic-key-here
   OPENAI_API_KEY=your-openai-key-here
   PINECONE_API_KEY=your-pinecone-key-here
   PINECONE_ENV=us-east-1
   JWT_SECRET_KEY=generate-32-char-string-here
   ALLOWED_ORIGINS=http://localhost:3000
   ```
   - Replace the placeholder values with your actual keys
   - For `JWT_SECRET_KEY`, use the generator below
   - Click **"Update Variables"**

6. **Generate Public URL:**
   - Go to **"Settings"** tab
   - Under **"Networking"**, click **"Generate Domain"**
   - Copy your domain (e.g., `blackswan-backend.up.railway.app`)
   - Save this URL for the frontend setup

### Step 2: Deploy Frontend to Vercel

1. **Create Vercel Account:**
   - Go to [Vercel.com](https://vercel.com)
   - Sign up with GitHub (recommended)
   - This links your GitHub automatically

2. **Import and Deploy:**
   - Click **"Add New..."** → **"Project"**
   - Click **"Import"** next to your forked repository
   - In **"Configure Project"** screen:
     - **Framework Preset**: Next.js (auto-detected ✓)
     - **Root Directory**: Click "Edit" and type `frontend`
     - **Build Command**: Leave as default
   - Don't click deploy yet!

3. **Add Environment Variables** (Still on Configure screen):
   - Open **"Environment Variables"** section
   - Add these one by one:
   
   | Name | Value |
   |------|-------|
   | `NEXTAUTH_SECRET` | Click "Generate" button or use generator below |
   | `NEXT_PUBLIC_API_URL` | Your Railway URL (e.g., `https://blackswan-backend.up.railway.app`) |
   | `NEXT_PUBLIC_SOCKET_URL` | Same URL but with `wss://` (e.g., `wss://blackswan-backend.up.railway.app`) |

   - Now click **"Deploy"**
   - Wait for build to complete (∼2 minutes)

4. **Get Your Frontend URL:**
   - After deployment completes
   - Copy your Vercel URL (e.g., `blackswan-frontend.vercel.app`)
   - You'll see it at the top of the deployment page

5. **Final Step - Update Railway CORS:**
   - Go back to Railway dashboard
   - Click your backend service → **"Variables"**
   - Update `ALLOWED_ORIGINS` to your Vercel URL:
     ```
     ALLOWED_ORIGINS=https://blackswan-frontend.vercel.app
     ```
   - Remove the `http://localhost:3000` if you don't need local access
   - Click **"Update Variables"**
   - Railway will automatically redeploy

### Step 3: Verify Everything Works

1. **Test Backend API:**
   - Visit: `https://your-backend.up.railway.app/health`
   - Should see: `{"status":"healthy","service":"black-swan-api"}`
   - Visit: `https://your-backend.up.railway.app/docs`
   - Should see: Interactive API documentation (Swagger UI)

2. **Test Frontend:**
   - Visit your Vercel URL
   - Should see: Black Swan dashboard with:
     - "Real-time Alerts" section
     - "System Status" showing all green
     - WebSocket connection indicator (green dot)

3. **First Time Setup:**
   - The dashboard will be empty (no alerts yet)
   - System actively monitors once deployed
   - Test alerts will appear as events are detected

## 🎉 Success! What Now?

Your Black Swan system is now:
- ✅ Monitoring crypto markets 24/7
- ✅ Analyzing events with AI
- ✅ Ready to send alerts

**Next Steps:**
1. Keep the dashboard open to see real-time alerts
2. Check the `/docs` endpoint to explore the API
3. Monitor your API usage in the respective dashboards
4. Consider setting up email/SMS alerts (coming soon)

## 🔑 Getting API Keys

### Anthropic (Claude)
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up/Login
3. Go to **"API Keys"**
4. Create new key

### OpenAI
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up/Login
3. Go to **"API Keys"**
4. Create new key

### Pinecone
1. Go to [pinecone.io](https://www.pinecone.io)
2. Sign up for free tier
3. Go to **"API Keys"**
4. Copy default key and environment

## 🔐 Generating Secure Keys

For `JWT_SECRET_KEY` and `NEXTAUTH_SECRET`, you need 32-character random strings.

### Easy Methods:

**🌐 Method 1: Web Generator (Easiest)**
1. Go to [RandomKeygen.com](https://randomkeygen.com/)
2. Scroll to **"CodeIgniter Encryption Keys"**
3. Copy any key from that section
4. Use the same key for both `JWT_SECRET_KEY` and `NEXTAUTH_SECRET`

**🔒 Method 2: Password Manager**
- Open your password manager (1Password, Bitwarden, etc.)
- Generate a 32+ character password
- Copy and use it

**💻 Method 3: Browser Console**
1. Right-click this page → **"Inspect"** → **"Console"**
2. Paste this code and press Enter:
```javascript
Array.from(crypto.getRandomValues(new Uint8Array(32))).map(b => b.toString(16).padStart(2, '0')).join('')
```
3. Copy the generated string

## ✅ Deployment Checklist

Before you start, make sure you have:

- [ ] GitHub account
- [ ] Forked this repository
- [ ] Railway account (free tier works)
- [ ] Vercel account (free tier works)
- [ ] API keys from:
  - [ ] Anthropic ($5 free credit on signup)
  - [ ] OpenAI ($5 free credit on signup)
  - [ ] Pinecone (free tier: 1 index)

## 💰 Costs & Limits

### Free Tier Limits:
- **Railway**: $5 free credit/month (enough for small projects)
- **Vercel**: Unlimited for personal use
- **Pinecone**: 1 index, 100k vectors
- **API Usage**: Pay-as-you-go (very low for testing)

### Estimated Monthly Costs:
- Light usage: ~$10-20
- Medium usage: ~$50-100
- Heavy usage: ~$200+

## 🔄 Automatic Deployments

Both Railway and Vercel automatically deploy when you push to GitHub:

1. **Make changes** to your forked repo
2. **Push to main branch**
3. **Watch deployments**:
   - Railway: Dashboard shows "Deploying..." status
   - Vercel: Creates preview for PRs, production for main
4. **Rollback if needed**: Both platforms keep deployment history

## 🛠️ Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (optional, can use Railway's)
- PostgreSQL (optional, can use Railway's)

### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# Run development server
python -m uvicorn main:app --reload

# Or use the helper script
./start_dev.sh
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local
# Edit .env.local

# Run development server
npm run dev
```

## 📁 Project Structure

```
.
├── backend/
│   ├── api/              # API routes
│   ├── config/           # Settings & configuration
│   ├── services/         # Microservices
│   │   ├── llm_orchestrator/  # AI coordination
│   │   └── ...
│   ├── shared/           # Shared utilities
│   ├── main.py          # FastAPI app
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── app/         # Next.js app router
    │   ├── components/  # React components
    │   ├── lib/        # Utilities
    │   └── stores/     # State management
    ├── package.json
    └── next.config.js
```

## 🔧 Configuration

### Required API Keys
- **Anthropic API**: For Claude Opus analysis
- **OpenAI API**: For GPT-4 verification
- **Pinecone**: For vector similarity search

### Optional Services
- **PostgreSQL**: Auto-provisioned by Railway
- **Redis**: Auto-provisioned by Railway
- **Monitoring**: Prometheus metrics at `/metrics`

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Data Sources  │     │     Railway     │     │     Vercel      │
│  News • Social  │────▶│   Backend API   │◀────│    Frontend     │
│  Market • Chain │     │   Python/Fast   │     │   Next.js/TS    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                          ▲
                               ▼                          │
                        ┌─────────────────┐               │
                        │   LLM Analysis  │               │
                        │ Claude • GPT-4  │               │
                        └─────────────────┘               │
                               │                          │
                               ▼                          │
                        ┌─────────────────┐               │
                        │  Redis Streams  │───WebSocket───┘
                        │  Event Queue    │
                        └─────────────────┘
```

**Tech Stack:**
- **Backend**: FastAPI + AsyncIO for high performance
- **Queue**: Redis Streams for event processing
- **AI**: Multi-agent LLM orchestration (Claude + GPT-4)
- **Frontend**: Next.js 14 with TypeScript
- **Real-time**: WebSocket for live alerts
- **Auth**: JWT with secure httpOnly cookies

## 🚨 Troubleshooting

### Common Deployment Issues

**Railway Issues:**
1. **Build fails** 
   - Check Python version (requires 3.11+)
   - Ensure all services are in `/backend` directory
   - Check logs in Railway dashboard → service → "Logs" tab

2. **Database connection errors**
   - Ensure PostgreSQL and Redis are added to project
   - Check if `DATABASE_URL` and `REDIS_URL` show in Variables
   - Services must be in same Railway project

3. **502 Bad Gateway**
   - Service might still be starting (wait 2-3 minutes)
   - Check if PORT environment variable is set
   - Verify health endpoint: `/health`

**Vercel Issues:**
1. **Build fails**
   - Ensure root directory is set to `frontend`
   - Check Node version (requires 18+)
   - Clear cache and redeploy

2. **API connection fails**
   - Verify `NEXT_PUBLIC_API_URL` starts with `https://`
   - Check if backend is deployed and running
   - Ensure CORS is configured correctly

3. **WebSocket errors**
   - Use `wss://` (not `ws://`) for production
   - Check browser console for detailed errors

**Quick Fixes:**
- **CORS errors**: Make sure `ALLOWED_ORIGINS` in Railway matches your Vercel URL exactly
- **Auth errors**: Keys must be exactly 32 characters (or longer)
- **Empty dashboard**: Check browser console, likely API connection issue

### Environment Variable Issues

**"Invalid API Key" Errors:**
1. Make sure you copied the entire key (no spaces)
2. Check you're using the right key:
   - Anthropic keys start with `sk-ant-`
   - OpenAI keys start with `sk-`
3. Verify keys are active in respective dashboards

**"NEXTAUTH_SECRET" Errors:**
- Must be at least 32 characters
- No spaces or special characters that might break
- Use the generators provided above

**WebSocket Connection Failed:**
- Ensure `NEXT_PUBLIC_SOCKET_URL` uses `wss://` (not `ws://`)
- Check Railway backend is running (green status)
- Verify the URL matches your Railway domain exactly

**CORS Errors in Console:**
1. Open Railway → Backend service → Variables
2. Check `ALLOWED_ORIGINS` value
3. Must match your Vercel URL exactly (including https://)
4. Multiple origins: comma-separated, no spaces

### Getting Help

1. **Check Logs:**
   - Railway: Dashboard → Service → "Logs" tab
   - Vercel: Dashboard → Project → "Functions" tab → "Logs"

2. **Debug Endpoints:**
   - Backend health: `https://your-backend.railway.app/health`
   - API docs: `https://your-backend.railway.app/docs`
   - Frontend API: Open browser DevTools → Network tab

3. **Community:**
   - Railway Discord: [discord.gg/railway](https://discord.gg/railway)
   - Vercel Discord: [discord.gg/vercel](https://discord.gg/vercel)

## 📝 License

MIT