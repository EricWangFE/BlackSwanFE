# Deployment Guide

This project uses Railway for backend and Vercel for frontend. Both platforms automatically deploy from GitHub.

## Automatic Deployment Setup

### Railway (Backend)

1. **Connect GitHub to Railway:**
   - In Railway dashboard, go to your project
   - Click **"Settings"** → **"GitHub"**
   - Connect your GitHub repository
   - Set **Root Directory** to `/backend`
   - Enable **"Auto Deploy"** for main branch

2. **Railway will automatically:**
   - Deploy on every push to main
   - Run health checks
   - Restart on failures
   - Show deployment logs

### Vercel (Frontend)

1. **Connect GitHub to Vercel:**
   - In Vercel dashboard, during project creation
   - Select your GitHub repository
   - Set **Root Directory** to `frontend`
   - Enable automatic deployments

2. **Vercel will automatically:**
   - Deploy on every push to main
   - Create preview deployments for PRs
   - Run build checks
   - Optimize for production

## Manual Deployment

### Deploy Backend to Railway

```bash
# Using Railway CLI
cd backend
railway up
```

### Deploy Frontend to Vercel

```bash
# Using Vercel CLI
cd frontend
vercel --prod
```

## Environment Variables

### Required for Railway:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `PINECONE_API_KEY`
- `PINECONE_ENV`
- `JWT_SECRET_KEY`
- `ALLOWED_ORIGINS`

### Required for Vercel:
- `NEXTAUTH_SECRET`
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_SOCKET_URL`

## Monitoring Deployments

### Railway
- View logs: Dashboard → Service → "Logs"
- View metrics: Dashboard → Service → "Metrics"
- Check health: `https://your-app.railway.app/health`

### Vercel
- View logs: Dashboard → Functions → "Logs"
- View analytics: Dashboard → "Analytics"
- Check build: Dashboard → "Deployments"

## Rollback

### Railway
- Dashboard → Service → "Deployments"
- Click on previous deployment
- Click "Redeploy"

### Vercel
- Dashboard → "Deployments"
- Find previous deployment
- Click "..." → "Promote to Production"