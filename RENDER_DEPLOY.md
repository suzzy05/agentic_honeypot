# Render Deployment Configuration

## 🚀 Deploy to Render

### Step 1: Go to Render
1. Visit: https://render.com
2. Sign up/login with GitHub
3. Click "New +" → "Web Service"

### Step 2: Connect Repository
1. Connect GitHub account
2. Select: `suzzy05/agentic_honeypot`
3. Branch: `master`

### Step 3: Configure Service
```
Name: agentic-honeypot
Environment: Python 3
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: python main.py
Instance Type: Free (starts with $7/month credit)
```

### Step 4: Environment Variables
Add these in Render dashboard:
```
API_KEY=YOUR_SECRET_API_KEY
GUVI_CALLBACK=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
PORT=8000
```

### Step 5: Deploy
- Click "Create Web Service"
- Render will automatically build and deploy
- Your API will be available at: `https://agentic-honeypot.onrender.com`

## 🧪 Test Your Deployed API

Once deployed, test with:
```bash
curl -X POST "https://agentic-honeypot.onrender.com/honeypot/message" \
  -H "x-api-key: YOUR_SECRET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "render-test",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked. Verify immediately.",
      "timestamp": 1770005528731
    }
  }'
```

## ✅ Features on Render
- ✅ Automatic SSL certificate
- ✅ Custom domain support
- ✅ Auto-deploy from GitHub
- ✅ Monitoring and logs
- ✅ Scale automatically

## 🎯 GUVI Evaluation Ready
Your deployed honeypot will:
- Detect scams globally 24/7
- Handle multi-turn conversations
- Extract intelligence automatically
- Send callbacks to GUVI endpoint
- Scale with traffic

**🏆 Ready for hackathon success!**
