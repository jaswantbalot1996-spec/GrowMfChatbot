# 🚀 Quick Deploy Guide

## In 5 Minutes: Deploy Your App

### Prerequisites
- GitHub account (already have)
- Render account (free) - https://render.com
- Vercel account (free) - https://vercel.com

---

## Step 1: Deploy Backend (Render) - 3 minutes

```bash
# 1. Go to https://render.com → Click "New+" → Web Service
# 2. Connect your GitHub repo (GrowMfChatbot)
# 3. Fill in:
#    Name: growmf-chatbot-api
#    Environment: Python 3
#    Branch: main
#    Build Command: pip install -r requirements.txt
#    Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT phase_4_extended_coverage.api_server_phase4:app

# 4. Add Environment Variables:
FLASK_ENV=production
OLLAMA_HOST=http://your-ollama-server:11434
CHROMA_API_KEY=your_chroma_api_key
MAX_TOKENS=150
ALLOWED_ORIGINS=http://localhost:3000,https://your-vercel-domain.vercel.app

# 5. Click "Create Web Service"
# 6. Wait 5 mins for deployment
# 7. Copy your API URL: https://growmf-chatbot-api.onrender.com
```

---

## Step 2: Deploy Frontend (Vercel) - 2 minutes

```bash
# 1. Go to https://vercel.com → Click "New Project"
# 2. Select GrowMfChatbot from GitHub
# 3. Set Root Directory: ./frontend
# 4. Add Environment Variables:
#    NEXT_PUBLIC_API_URL=https://growmf-chatbot-api.onrender.com
# 5. Click "Deploy"
# 6. Wait 2 mins
# 7. Your app is live! 🎉
#    https://your-project-name.vercel.app
```

---

## Step 3: Test Your Deployment

```bash
# Open in browser:
# https://your-project-name.vercel.app

# Try asking:
# "What is ELSS?"

# Expected: Response in 10-15 seconds
```

---

## What's Deployed?

```
┌─────────────────────────────────────┐
│      Frontend (Vercel)              │
│  Next.js App - React Components     │
│  https://app.vercel.app             │
└──────────────┬──────────────────────┘
               │
               │ API Calls
               │
┌──────────────▼──────────────────────┐
│     Backend (Render)                │
│  Flask API Server + Ollama LLM      │
│  https://api.onrender.com           │
└─────────────────────────────────────┘
```

---

## Auto-Deploy with GitHub

After every push to `main`:
✅ Backend auto-deploys to Render  
✅ Frontend auto-deploys to Vercel

Just push! No manual deploys needed.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Cannot connect" | Verify `NEXT_PUBLIC_API_URL` is correct |
| CORS errors | Update `ALLOWED_ORIGINS` on backend |
| Slow responses | Check `MAX_TOKENS=150` is set |
| 404 errors | Ensure backend health: `{api-url}/health` |

---

## Cost

| Service | Cost | Free Tier |
|---------|------|-----------|
| Render | $7/mo | ✅ Free (limited) |
| Vercel | $0 | ✅ Free tier |
| **Total** | **~$7/mo** | **Mostly Free** |

---

## Files Created

```
frontend/                          # Next.js app
├── app/
│   ├── page.js                    # Main chat page
│   ├── globals.css                # Styling
│   └── layout.js                  # Layout
├── package.json
├── next.config.js
├── Dockerfile
└── README.md

DEPLOYMENT.md                       # Full deployment guide
DEPLOYMENT_CHECKLIST.md             # Step-by-step checklist
Dockerfile                          # Backend Docker config
Procfile                           # Render config
requirements.txt                    # Python dependencies
.github/workflows/
├── deploy-backend.yml             # Auto-deploy backend
└── deploy-frontend.yml            # Auto-deploy frontend
```

---

## Keys to Success ✅

1. **Environment Variables**: Double-check all are set
2. **CORS Configuration**: Allow your Vercel domain
3. **API Health**: Test `/health` endpoint
4. **Error Logs**: Check Render logs if something fails
5. **Clear Cache**: Clear browser cache if UI won't update

---

## Next Steps

1. ✅ Commit all changes: `git add . && git commit -m "Setup deployment"`
2. ✅ Push to main: `git push origin main`
3. ✅ Create Render service
4. ✅ Create Vercel project
5. ✅ Set environment variables
6. ✅ Test the live app!

---

**Questions?**
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide
- Check [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for verification
- Render Support: https://render.com/docs
- Vercel Support: https://vercel.com/docs

---

**Happy Deploying! 🚀**
