# Agentic Honeypot - Global Deployment

## 🚀 Quick Deploy Options

### Option 1: Railway (Recommended - Free)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway up
```

### Option 2: Render (Free Tier)
```bash
# Install Render CLI
npm install -g render-cli

# Deploy
render deploy
```

### Option 3: Vercel (Free)
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### Option 4: Heroku (Free Tier)
```bash
# Install Heroku CLI
# Create app
heroku create your-honeypot-app

# Deploy
heroku container:push web
heroku container:release web
```

## 📋 Prerequisites

1. **Create GitHub Repository:**
   - Go to https://github.com/suzzy05
   - Click "New repository"
   - Name: `agentic-honeypot`
   - Make it Public
   - Click "Create repository"

2. **Push Code:**
   ```bash
   git remote set-url origin https://github.com/suzzy05/agentic-honeypot.git
   git push -u origin master
   ```

## 🔧 Environment Variables (Required for all platforms)

Set these in your deployment platform:

```bash
API_KEY=YOUR_SECRET_API_KEY
GUVI_CALLBACK=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
PORT=8000
```

## 🌐 After Deployment

Your API will be available at:
- Railway: `https://your-app-name.up.railway.app`
- Render: `https://your-app-name.onrender.com`
- Vercel: `https://your-app-name.vercel.app`
- Heroku: `https://your-app-name.herokuapp.com`

## 🧪 Test Your Deployed API

```bash
curl -X POST "https://your-deployed-url/honeypot/message" \
  -H "x-api-key: YOUR_SECRET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-global",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked. Verify immediately.",
      "timestamp": 1770005528731
    }
  }'
```

## 📊 Monitoring

All platforms provide:
- ✅ Auto-scaling
- ✅ SSL certificates
- ✅ Monitoring
- ✅ Logs
- ✅ Custom domains

## 🎯 Ready for GUVI Evaluation

Once deployed, your honeypot will:
- ✅ Detect scams globally
- ✅ Handle multi-turn conversations
- ✅ Extract intelligence
- ✅ Send callbacks to GUVI
- ✅ Scale automatically

**Choose Railway for fastest deployment!**
