# Black Swan Event Detection System - Replit Edition

![CI](https://github.com/EricWangFE/BlackSwanFE/workflows/CI/badge.svg)
[![Run on Replit](https://replit.com/badge/github/EricWangFE/BlackSwanFE)](https://replit.com/github/EricWangFE/BlackSwanFE)

Real-time cryptocurrency black swan event detection using multi-agent LLMs - now with one-click Replit deployment!

## 🎯 What This App Does

**Black Swan** monitors crypto markets 24/7 and alerts you to potential catastrophic events BEFORE they fully unfold:

- 📊 **Real-time Monitoring**: Tracks news, social media, and market data
- 🤖 **AI Analysis**: Multiple LLMs analyze events for severity and impact
- 🚨 **Smart Alerts**: Get notified only when something significant happens
- 📈 **Risk Assessment**: Detailed analysis with confidence scores
- ⚡ **WebSocket Updates**: Live dashboard with instant updates

## 🚀 Deploy in 60 Seconds with Replit

### Prerequisites
- [Replit account](https://replit.com) (free)
- API keys from:
  - [Anthropic](https://console.anthropic.com) (Claude)
  - [OpenAI](https://platform.openai.com) (GPT-4)
  - [Pinecone](https://pinecone.io) (Vector DB)

### One-Click Deploy

1. **Click the "Run on Replit" button above** or go to:
   ```
   https://replit.com/github/EricWangFE/BlackSwanFE
   ```

2. **Import the Repository**
   - Replit will automatically import from the `replit-deployment` branch
   - Wait for the import to complete (∼30 seconds)

3. **Add Your API Keys**
   - Click the **🔒 Secrets** tab (lock icon in left sidebar)
   - Add these secrets one by one:
   
   | Key | Value |
   |-----|-------|
   | `ANTHROPIC_API_KEY` | Your Anthropic API key |
   | `OPENAI_API_KEY` | Your OpenAI API key |
   | `PINECONE_API_KEY` | Your Pinecone API key |
   | `PINECONE_ENV` | `us-east-1` (or your region) |
   | `JWT_SECRET_KEY` | Generate 32-char string (see below) |
   | `NEXTAUTH_SECRET` | Same as JWT_SECRET_KEY |

4. **Add PostgreSQL Database** (Optional but recommended)
   - In Replit, click **Tools** → **Database**
   - Click **Create Database** → Select **PostgreSQL**
   - It will automatically set `DATABASE_URL`

5. **Click the Big Green "Run" Button**
   - First run will take 2-3 minutes (installing dependencies)
   - You'll see the startup logs in the console
   - When you see "✅ Black Swan System is running!" it's ready

6. **Access Your App**
   - Click **"Open in a new tab"** button (↗️ icon)
   - Or visit: `https://[your-repl-name].[your-username].repl.co`
   - API Docs: `https://[your-repl-name].[your-username].repl.co:8000/docs`

## 🔐 Generating Secure Keys

For `JWT_SECRET_KEY` and `NEXTAUTH_SECRET`, you need a 32-character random string:

**Option 1: Use Replit Shell**
```bash
openssl rand -hex 32
```

**Option 2: Online Generator**
- Visit [RandomKeygen.com](https://randomkeygen.com/)
- Copy any key from "CodeIgniter Encryption Keys"

**Option 3: Use this JavaScript** (paste in browser console):
```javascript
Array.from(crypto.getRandomValues(new Uint8Array(32))).map(b => b.toString(16).padStart(2, '0')).join('')
```

## 🎮 Using the App

Once deployed, your Black Swan system will:

1. **Monitor Markets** - Continuously scan for anomalies
2. **Analyze Events** - Use AI to assess severity
3. **Send Alerts** - Display on dashboard in real-time
4. **Provide Analysis** - Detailed breakdown of risks

### Dashboard Features
- **Real-time Alerts Feed** - Live updates via WebSocket
- **System Status** - Monitor AI models and data streams
- **Alert History** - Track past events
- **Risk Metrics** - Confidence scores and severity levels

## 🛠️ Configuration

### Environment Variables (Set in Replit Secrets)

**Required:**
- `ANTHROPIC_API_KEY` - For Claude analysis
- `OPENAI_API_KEY` - For GPT-4 verification
- `PINECONE_API_KEY` - For vector similarity search
- `JWT_SECRET_KEY` - For authentication
- `NEXTAUTH_SECRET` - For session management

**Optional:**
- `DATABASE_URL` - Auto-set if you add PostgreSQL
- Custom configuration in `backend/config/settings.py`

### Adjusting Settings

1. **Rate Limits**: Edit `backend/shared/middleware/rate_limit.py`
2. **AI Models**: Configure in `backend/services/llm_orchestrator/orchestrator.py`
3. **Alert Thresholds**: Modify in `backend/config/settings.py`

## 🔄 Updating Your App

1. **Make changes** in your GitHub repository
2. **In Replit**, click the **Git** tab
3. Click **Pull** to get latest changes
4. Click **Run** to restart with updates

Or use Replit Shell:
```bash
git pull origin replit-deployment
```

## 💰 Costs

### Replit Costs
- **Free Tier**: Works for testing and light use
- **Hacker Plan** ($7/mo): Better performance, always-on
- **Cycles**: Pay-as-you-go for compute time

### API Costs (Pay-per-use)
- **Anthropic/OpenAI**: ~$0.01-0.03 per analysis
- **Pinecone**: Free tier includes 100K vectors

### Estimated Monthly Costs
- Testing: Free - $10
- Light use: $10-30
- Production: $50-100+

## 🚨 Troubleshooting

### Common Issues

**"Module not found" errors**
- Click **Stop** then **Run** again
- Dependencies might still be installing

**Database connection errors**
- Add PostgreSQL via Replit's database tool
- Or it will use SQLite locally

**API key errors**
- Check Secrets tab - keys must be exact
- No extra spaces or quotes

**Frontend not loading**
- Wait 2-3 minutes after clicking Run
- Check console for "Frontend running on port 3000"

**WebSocket connection failed**
- Normal during startup, will reconnect
- Check if backend is running on port 8000

### Debug Commands (Run in Shell)

Check backend:
```bash
curl http://localhost:8000/health
```

Check frontend:
```bash
curl http://localhost:3000
```

View logs:
```bash
tail -f logs/*.log
```

## 📁 Project Structure

```
.
├── backend/               # FastAPI backend
│   ├── api/              # API routes
│   ├── services/         # Core services
│   │   └── llm_orchestrator/  # AI coordination
│   ├── shared/           # Shared utilities
│   └── main.py          # FastAPI app
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/         # App router pages
│   │   ├── components/  # React components
│   │   └── lib/         # Utilities
│   └── package.json
├── run.sh               # Replit startup script
├── .replit              # Replit configuration
└── replit.nix          # Nix dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Make your changes
4. Push to your fork
5. Open a Pull Request to `replit-deployment` branch

## 📝 License

MIT - feel free to use this for your own projects!

---

**Need Help?** 
- Check the [API Docs](https://your-app.repl.co:8000/docs)
- View [Console Logs](https://your-app.repl.co/__logs)
- Ask in [Replit Discord](https://discord.gg/replit)