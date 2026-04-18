# 🚀 GrowMF Chatbot - Deployment Guide

## Architecture
- **Frontend**: Next.js → Vercel
- **Backend**: Flask → Render
- **LLM**: Ollama (must be running separately)
- **Vector DB**: Chroma Cloud

---

## Part 1: Backend Deployment (Render)

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Step 2: Create PostgreSQL Database (Optional, if needed)
1. In Render dashboard, click **"New"** → **"PostgreSQL"**
2. Set:
   - Name: `growmf-db`
   - PostgreSQL Version: **15**
   - Region: Closest to you
3. Copy the **Internal Database URL** (will use in environment variables)

### Step 3: Deploy Flask Backend
1. In Render, click **"New"** → **"Web Service"**
2. Select **"Connect a Repository"** → choose `GrowMfChatbot`
3. Configure:
   - **Name**: `growmf-chatbot-api`
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```
     gunicorn -w 4 -b 0.0.0.0:$PORT phase_4_extended_coverage.api_server_phase4:app
     ```

4. **Add Environment Variables** (in Settings → Environment):
   ```
   FLASK_ENV=production
   OLLAMA_HOST=<your-ollama-server-url>
   CHROMA_API_KEY=<your-chroma-api-key>
   MAX_TOKENS=150
   ```

5. Click **"Create Web Service"**
6. Wait for deployment (~5 min). Copy the URL (e.g., `https://growmf-chatbot-api.onrender.com`)

### Step 4: Configure CORS
Your Flask app already has CORS enabled, but verify in `api_server_phase4.py`:
```python
CORS(app, origins=["https://yourdomain.vercel.app", "http://localhost:3000"])
```

---

## Part 2: Frontend Deployment (Vercel)

### Step 1: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Authorize Vercel to access your repositories

### Step 2: Deploy Next.js Frontend
1. Click **"New Project"**
2. Select your `GrowMfChatbot` repository
3. Under **"Root Directory"**, set to `./frontend`
4. Click **"Import"**

### Step 3: Set Environment Variables
In Vercel Project Settings → Environment Variables:
```
NEXT_PUBLIC_API_URL=https://growmf-chatbot-api.onrender.com
```

### Step 4: Deploy
Click **"Deploy"** and wait (~2 min)

Your app will be available at: `https://<project-name>.vercel.app`

---

## Part 3: GitHub Actions (Optional - Auto Deploy)

### Step 1: Add Render API Key
1. Go to Render → Account Settings → API Keys
2. Create new key and copy it
3. Add to GitHub Secrets: `RENDER_API_KEY`

### Step 2: Add Vercel Token
1. Go to Vercel Settings → Tokens
2. Create new token
3. Add to GitHub Secrets:
   - `VERCEL_TOKEN`
   - `VERCEL_ORG_ID`
   - `VERCEL_PROJECT_ID`

### Step 3: Auto-Deploy on Push
Workflows are already configured in `.github/workflows/`:
- `deploy-frontend.yml` - Deploys when `frontend/**` changes
- `deploy-backend.yml` - Deploys when `phase_4_extended_coverage/**` changes

Push to `main` branch and both will auto-deploy!

---

## Part 4: Local Testing Before Deploy

### Test Backend Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
python phase_4_extended_coverage/api_server_phase4.py 8000

# Test health
curl http://localhost:8000/health

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is ELSS?","language":"en"}'
```

### Test Frontend Locally
```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Open http://localhost:3000
```

---

## Part 5: Production Checklist

- [ ] Backend deployed on Render
- [ ] Frontend deployed on Vercel
- [ ] Backend URL set in frontend `.env.production`
- [ ] CORS enabled for Vercel domain
- [ ] Environment variables configured on both services
- [ ] GitHub Actions secrets configured
- [ ] Database credentials stored securely
- [ ] API rate limiting configured (if needed)
- [ ] Error monitoring enabled (Sentry, etc.)
- [ ] SSL/HTTPS enabled (automatic on both platforms)

---

## Monitoring & Logs

### Render Logs
1. Go to your service in Render
2. Click **"Logs"** tab
3. View real-time logs and errors

### Vercel Logs
1. Go to your project in Vercel
2. Click **"Deployments"**
3. Select deployment → **"Function Logs"**

---

## Troubleshooting

### Backend not responding
1. Check environment variables are set correctly
2. Verify Ollama service is running (if self-hosted)
3. Check Render logs for errors
4. Restart service in Render dashboard

### Frontend shows "Cannot connect"
1. Verify `NEXT_PUBLIC_API_URL` in Vercel env vars
2. Check backend health: `curl https://growmf-chatbot-api.onrender.com/health`
3. Clear browser cache
4. Check browser console for CORS errors

### Slow responses
1. Check `MAX_TOKENS` setting on backend
2. Verify Chroma Cloud connectivity
3. Monitor Render CPU/memory usage
4. Scale up Render instance if needed

---

## Subsequent Deployments

### To deploy backend changes:
```bash
git add phase_4_extended_coverage/
git commit -m "Update API"
git push origin main
```
→ Render auto-deploys (if GitHub Actions enabled)

### To deploy frontend changes:
```bash
git add frontend/
git commit -m "Update UI"
git push origin main
```
→ Vercel auto-deploys

---

## Cost Estimation (Monthly)

| Service | Plan | Price |
|---------|------|-------|
| Render (Backend) | Starter (~$7/mo) | $7 |
| Vercel (Frontend) | Free tier | $0-20 |
| Chroma Cloud | Usage-based | $0-10 |
| **Total** | | **~$7-30/mo** |

---

## Next Steps

1. **Push to GitHub**: Commit all changes to `main` branch
2. **Deploy Backend**: Create Render service
3. **Deploy Frontend**: Create Vercel project
4. **Configure Domains**: (Optional) Add custom domains
5. **Monitor**: Set up error tracking and analytics

---

For questions, check the service documentation:
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
