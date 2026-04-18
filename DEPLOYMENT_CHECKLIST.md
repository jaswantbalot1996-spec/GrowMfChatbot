# 📋 Deployment Checklist

## ✅ Pre-Deployment Setup

- [ ] All code committed to GitHub `main` branch
- [ ] `.env.backend.example` reviewed and values understood
- [ ] `.env.frontend.example` reviewed and values understood
- [ ] `requirements.txt` has all Python dependencies
- [ ] `frontend/package.json` has all npm dependencies
- [ ] GitHub Actions workflows enabled in repository settings

## 🔧 Backend Setup (Render)

### Create Render Account & Service
- [ ] Create account at [render.com](https://render.com)
- [ ] Connect GitHub repository
- [ ] Create Web Service
  - [ ] Name: `growmf-chatbot-api`
  - [ ] Environment: Python 3
  - [ ] Build Command: `pip install -r requirements.txt`
  - [ ] Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT phase_4_extended_coverage.api_server_phase4:app`
  - [ ] Region: Select closest region

### Configure Backend Environment
- [ ] Set `FLASK_ENV=production`
- [ ] Set `OLLAMA_HOST` (your Ollama server URL)
- [ ] Set `CHROMA_API_KEY` (your Chroma Cloud API key)
- [ ] Set `MAX_TOKENS=150`
- [ ] Set `ALLOWED_ORIGINS=https://yourdomain.vercel.app`
- [ ] Verify health endpoint: `https://<service-url>.onrender.com/health`

### Verify Backend Deployment
- [ ] API responds to health check (200 status)
- [ ] Test query endpoint returns valid JSON
- [ ] Check real-time logs in Render dashboard
- [ ] Copy final URL (e.g., `https://growmf-chatbot-api.onrender.com`)

## 🎨 Frontend Setup (Vercel)

### Create Vercel Account & Project
- [ ] Create account at [vercel.com](https://vercel.com)
- [ ] Click "New Project"
- [ ] Import `GrowMfChatbot` repository from GitHub
- [ ] Set Root Directory: `./frontend`

### Configure Frontend Environment
- [ ] Set `NEXT_PUBLIC_API_URL={your-render-backend-url}`
  - Example: `https://growmf-chatbot-api.onrender.com`
- [ ] Verify production build passes
- [ ] Check preview deployment works

### Verify Frontend Deployment
- [ ] Site loads without errors at Vercel domain
- [ ] Can submit queries and receive responses
- [ ] Language switching works (EN/HI)
- [ ] Filters display correctly
- [ ] Copy final URL (e.g., `https://growmf-chatbot.vercel.app`)

## 🤖 Update Backend CORS

- [ ] Update `ALLOWED_ORIGINS` in Render environment to include Vercel domain
- [ ] Restart backend service in Render dashboard
- [ ] Test frontend-backend communication

## 🔄 GitHub Actions (Auto-Deploy)

### Backend Auto-Deploy
- [ ] Add `RENDER_API_KEY` to GitHub Secrets
- [ ] Add `RENDER_SERVICE_ID` to GitHub Secrets
- [ ] Test: Push to `main` branch containing backend changes
- [ ] Verify auto-deployment in Render logs

### Frontend Auto-Deploy
- [ ] Add `VERCEL_TOKEN` to GitHub Secrets
- [ ] Add `VERCEL_ORG_ID` to GitHub Secrets
- [ ] Add `VERCEL_PROJECT_ID` to GitHub Secrets
- [ ] Test: Push to `main` branch containing frontend changes
- [ ] Verify auto-deployment in Vercel dashboard

## 🧪 End-to-End Testing

### Test Production Environment
- [ ] Open Vercel frontend URL in browser
- [ ] Submit test query: "What is ELSS?"
- [ ] Verify response appears
- [ ] Check response time (should be < 30 seconds)
- [ ] Test language switching
- [ ] Test filters
- [ ] Check console for errors

### Performance Validation
- [ ] Response latency < 30 seconds
- [ ] No CORS errors in console
- [ ] All UI interactive elements work
- [ ] Images/styling load correctly
- [ ] Mobile responsive (test on mobile)

## 📊 Monitoring Setup

### Render Monitoring
- [ ] Enable error tracking (Sentry optional)
- [ ] Set up log aggregation (Datadog optional)
- [ ] Create uptime monitors
- [ ] Alert on failures

### Vercel Monitoring
- [ ] Enable Web Analytics
- [ ] Set up error reporting
- [ ] Monitor build times
- [ ] Check performance metrics

## 🔒 Security Checklist

- [ ] No sensitive credentials in code/git
- [ ] Environment variables used for all secrets
- [ ] API rate limiting considered
- [ ] HTTPS enabled (automatic on both)
- [ ] CORS properly configured
- [ ] Input validation active
- [ ] Error messages don't leak sensitive info

## 📝 Documentation

- [ ] README.md updated with deployed URLs
- [ ] DEPLOYMENT.md complete and accurate
- [ ] API documentation up to date
- [ ] Environment variables documented
- [ ] Troubleshooting guide created

## 🚀 Post-Deployment

- [ ] Share deployed URL with stakeholders
- [ ] Create monitoring dashboard
- [ ] Document rollback procedures
- [ ] Plan scaling if needed
- [ ] Set up automated backups (if DB used)
- [ ] Schedule regular health checks

## 🐛 Troubleshooting Ready

- [ ] Have Render logs open
- [ ] Have Vercel logs open
- [ ] Browser DevTools console monitored
- [ ] Network tab ready to inspect requests
- [ ] CORS issues checklist prepared

---

**Status**: Ready for deployment ✅

**Next Steps**:
1. Create Render service for backend
2. Create Vercel project for frontend
3. Configure environment variables
4. Test end-to-end
5. Enable GitHub Actions

---

**Need Help?**
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Django Deployment: See DEPLOYMENT.md
