# Check Your Slack Bot Deployment Status

Since your Slack Bot web service **already exists** on Render, it should have automatically detected your recent git push!

---

## 🔍 Step 1: Check Deployment Status in Render

### Go to Render Dashboard:
1. Open: https://dashboard.render.com
2. Look for your **Slack Bot service** (probably named `slackoms-bot` or similar)
3. Click on it

### What to Look For:

#### In the "Events" Tab (left sidebar):
You should see one of these:

**✅ Scenario A: Auto-Deploy is Working**
```
🔄 Deploying... (In progress)
   └─ Detected push to main branch
   └─ Build started
   └─ Installing dependencies
   └─ Starting server...
```
**→ Wait 5-10 minutes for it to complete!**

**✅ Scenario B: Already Deployed**
```
✅ Deploy live (5 minutes ago)
   └─ Commit: slack bot for paper trading (1374032)
```
**→ Your latest code is already live!**

**⚠️ Scenario C: No New Deployment**
```
✅ Deploy live (2 days ago)
   └─ Commit: [old commit message]
```
**→ Auto-deploy might be OFF. See Step 2.**

---

## 🔧 Step 2: Verify Auto-Deploy is Enabled

If you're in **Scenario C** (no new deployment):

1. In your Slack Bot service dashboard on Render
2. Click **"Settings"** tab (left sidebar)
3. Scroll to **"Build & Deploy"** section
4. Look for **"Auto-Deploy"**:
   - If it says **"No"** → Click **"Edit"** and change to **"Yes"**
   - If it says **"Yes"** → Something else is wrong

---

## 🚀 Step 3: Manually Trigger Deploy (If Needed)

If auto-deploy didn't work or is OFF:

1. Go to your Slack Bot service dashboard
2. Top right corner: Click **"Manual Deploy"** dropdown
3. Select **"Deploy latest commit"**
4. Confirm
5. Wait 5-10 minutes

---

## 🧪 Step 4: Test When Deployment Completes

Once you see **"Deploy live"** status:

### Get Your Bot URL:
At the top of the service page, you'll see:
```
https://[your-bot-name].onrender.com
```
Copy this URL!

### Test the Bot:
```bash
# Test bot health
curl https://[your-bot-name].onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "SlackOMS Bot",
  "oms_api_connected": true
}
```

---

## 📝 Step 5: Update Slack URLs (Critical!)

Even if your bot is deployed, Slack still needs to know where it is!

### Update These URLs in Slack:

1. Go to: https://api.slack.com/apps
2. Click on your **"Paper Trading Bot"**
3. **Update Slash Command URL**:
   - Go to **"Slash Commands"** → Click `/trade` → **"Request URL"**
   - Set to: `https://[your-bot-name].onrender.com/slack/commands`
   - Click **"Save"**

4. **Update Interactivity URL**:
   - Go to **"Interactivity & Shortcuts"** → **"Request URL"**
   - Set to: `https://[your-bot-name].onrender.com/slack/interactions`
   - Click **"Save Changes"**

---

## ✅ Step 6: Test in Slack!

Open Slack and type:
```
/trade AAPL
```

### Expected Result:
- ✅ A modal (form) pops up
- ✅ Fill it in and submit
- ✅ See confirmation message with trade details

### If You Get Errors:

**"dispatch_failed"**
- Bot URL not updated in Slack
- Go back to Step 5

**"Invalid signature"**
- Wrong `SLACK_SIGNING_SECRET` in Render
- Check environment variables

**"OMS API not reachable" in bot logs**
- Wrong `OMS_API_URL` or `OMS_API_KEY`
- Check environment variables

---

## 🎯 Quick Checklist

- [ ] Slack Bot service exists on Render
- [ ] Recent deployment visible in "Events" tab
- [ ] Auto-deploy is enabled (if not, trigger manual deploy)
- [ ] Deployment status shows "Deploy live"
- [ ] Bot health endpoint returns 200 OK
- [ ] Slack slash command URL updated
- [ ] Slack interactivity URL updated
- [ ] `/trade` command works in Slack!

---

## 🆘 Common Issues

### Issue: Service exists but no code inside
**Symptom**: Service dashboard shows "No deployments yet"  
**Fix**: The service was created but never connected to GitHub
- Go to Settings → Build & Deploy
- Connect your GitHub repo
- Set Root Directory to `slack-bot`
- Trigger manual deploy

### Issue: Wrong code is deployed
**Symptom**: Old commit is deployed  
**Fix**: Manually deploy latest commit (Step 3)

### Issue: Build fails
**Symptom**: Deployment fails with errors  
**Fix**: Check logs for errors (usually missing environment variables)
- Go to "Logs" tab
- Look for error messages
- Verify all 5 environment variables are set:
  - `SLACK_BOT_TOKEN`
  - `SLACK_SIGNING_SECRET`
  - `OMS_API_URL`
  - `OMS_API_KEY`
  - `ENVIRONMENT`

---

## 📊 What's Your Current Status?

Tell me what you see when you check the Render dashboard:
1. Is there a recent deployment?
2. What's the status? (Deploying/Deploy live/Failed)
3. What's the bot URL?

Then we can proceed accordingly! 🚀


