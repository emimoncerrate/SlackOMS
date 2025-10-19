# Render Auto-Deploy Guide

## What is Auto-Deploy?

Auto-deploy means Render automatically rebuilds and redeploys your service whenever you push new code to GitHub.

---

## Check Auto-Deploy Status (Existing Services)

### For Your OMS API

1. Go to: https://dashboard.render.com
2. Click on **`slackoms-api`** service
3. Click **"Settings"** tab (left sidebar)
4. Scroll to **"Build & Deploy"** section
5. Look for **"Auto-Deploy"** setting:
   - ✅ **Yes** = Automatic updates on every push
   - ❌ **No** = Manual deploy only

### If Auto-Deploy is ON (Default):
- Every `git push` triggers a new deployment automatically
- You'll see a new deployment in the "Events" tab
- Wait 5-10 minutes for it to complete
- No action needed from you!

### If Auto-Deploy is OFF:
You need to manually trigger deploys:
1. Go to your service dashboard
2. Click **"Manual Deploy"** (top right)
3. Select **"Deploy latest commit"**
4. Wait for deployment to finish

---

## For NEW Services (Slack Bot)

Your **Slack Bot is NOT deployed yet!**

You need to **create it first** on Render:

### Steps:
1. Open Render Dashboard: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo (`SlackOMS`)
4. Configure the service:
   - **Root Directory**: `slack-bot` ⚠️ IMPORTANT!
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
5. Add environment variables (5 required)
6. Click **"Create Web Service"**

**After creation**, auto-deploy will be enabled by default for future pushes.

---

## Current Status of Your Project

| Service | Status | Auto-Deploy |
|---------|--------|-------------|
| **OMS API** | ✅ Deployed & Running | Likely ON (check settings) |
| **Slack Bot** | ❌ Not deployed yet | N/A - needs to be created |

---

## What Happens After Your Recent Push?

Since you just pushed "slack bot for paper trading" to GitHub:

### OMS API (if auto-deploy is ON):
- ✅ Render detected the push
- 🔄 It's rebuilding the OMS API now (or will soon)
- ⏱️ Check the "Events" tab to see progress
- **Note**: No changes to OMS API code, so it should redeploy quickly

### Slack Bot:
- ❌ Nothing happens yet
- You need to manually create the service first
- Follow the steps in `DEPLOY_BOT_NOW.md`

---

## How to See Deployment Status

### Live Deployment Monitoring:

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on your service** (`slackoms-api`)
3. **Click "Events" tab** (left sidebar)

You'll see:
```
🔄 Deploying...
   └─ In progress  (detected push from GitHub)
   └─ Build started
   └─ Installing dependencies
   └─ Starting server
✅ Deploy successful!
```

### If You See "Deploy live" Status:
- Your recent push is already deployed!
- The service is running the latest code

---

## Manual Deploy (If Needed)

If auto-deploy is OFF, or you want to force a redeploy:

1. Go to your service in Render Dashboard
2. Top right: Click **"Manual Deploy"** dropdown
3. Select **"Deploy latest commit"**
4. Confirm and wait for deployment

---

## Best Practice

**Keep auto-deploy ON** unless you have a specific reason to turn it off:
- ✅ Instant updates when you push code
- ✅ No manual steps needed
- ✅ Always in sync with your GitHub repo
- ⚠️ Just make sure your code is tested before pushing!

---

## Next Steps for You

1. **Check OMS API**:
   - Visit: https://dashboard.render.com
   - See if a new deployment is running
   - Wait for it to complete (if any)

2. **Deploy Slack Bot**:
   - Follow: `DEPLOY_BOT_NOW.md`
   - Create the new service
   - Enable auto-deploy (it's default)

3. **Test everything**:
   - OMS API: `curl https://slackoms-api.onrender.com/health`
   - After bot is deployed: `/trade` in Slack

---

## Quick Commands to Check Deployment

```bash
# Check if OMS API is running (should return 200)
curl -I https://slackoms-api.onrender.com/health

# Check if it's using latest code (check version in response)
curl https://slackoms-api.onrender.com/
```

---

**TL;DR**: 
- Your OMS API likely auto-updated already (or is updating now)
- Your Slack Bot needs to be manually created first
- After creation, both will auto-deploy on future pushes! ✨


