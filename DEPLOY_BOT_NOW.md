# 🚀 Deploy Your Slack Bot RIGHT NOW!

## Your Credentials (Ready to Use!)

⚠️ **IMPORTANT**: Get your actual credentials from:
- **Slack Bot Token**: https://api.slack.com/apps → Your App → "OAuth & Permissions" (starts with `xoxb-`)
- **Slack Signing Secret**: https://api.slack.com/apps → Your App → "Basic Information" → "App Credentials"
- **OMS API URL**: `https://slackoms-api.onrender.com`
- **OMS API Key**: From your local `oms-api/.env` file or Render Dashboard

---

## Quick Deployment Steps (10 minutes!)

### 1. Open Render Dashboard

Go to: **https://dashboard.render.com**

### 2. Create New Web Service

- Click **"New +"** (top right)
- Select **"Web Service"**

### 3. Connect Your GitHub Repository

**If you haven't pushed to GitHub yet:**
```bash
cd /Users/emily/mybuilds/SlackOMS
git add .
git commit -m "Add Slack Bot for paper trading"
git push origin main
```

**Then in Render:**
- Click **"Connect account"** if needed
- Find your `SlackOMS` repository
- Click **"Connect"**

### 4. Configure the Service

Fill in these **EXACT** settings:

| Field | Value |
|-------|-------|
| **Name** | `slackoms-bot` |
| **Region** | Same as your OMS API (check your OMS API service) |
| **Branch** | `main` |
| **Root Directory** | `slack-bot` ⚠️ IMPORTANT! |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python main.py` |
| **Instance Type** | `Free` |

### 5. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these **5 variables** (get your actual values from Slack API dashboard and local `.env` file!):

| Key | Value |
|-----|-------|
| `SLACK_BOT_TOKEN` | Your token from Slack (starts with `xoxb-`) |
| `SLACK_SIGNING_SECRET` | Your signing secret from Slack |
| `OMS_API_URL` | `https://slackoms-api.onrender.com` |
| `OMS_API_KEY` | Your API key from `oms-api/.env` |
| `ENVIRONMENT` | `production` |

### 6. Deploy!

- Click **"Create Web Service"**
- Wait 5-10 minutes for deployment
- Watch the logs - you should see:
  ```
  SlackOMS Bot v1.0.0
  Environment: production
  ✅ OMS API is reachable
  Starting bot server on 0.0.0.0:5000
  ```

### 7. Get Your Bot URL

Once deployed, your bot URL will be:
**`https://slackoms-bot.onrender.com`**

Copy this! You need it for Step 3.

---

## Step 3: Update Slack URLs (5 minutes!)

Now you need to tell Slack where your bot lives!

### 1. Go Back to Slack API

- Open: https://api.slack.com/apps
- Click on **"Paper Trading Bot"**

### 2. Update Slash Command URL

- Go to **"Slash Commands"** (left sidebar)
- Click on **`/trade`** to edit
- Change **Request URL** to: `https://slackoms-bot.onrender.com/slack/commands`
- Click **"Save"**

### 3. Update Interactivity URL

- Go to **"Interactivity & Shortcuts"** (left sidebar)
- Change **Request URL** to: `https://slackoms-bot.onrender.com/slack/interactions`
- Click **"Save Changes"**

### 4. Reinstall (if prompted)

- Go to **"Install App"**
- If you see "Reinstall App", click it
- Click **"Allow"**

---

## Step 4: Test It! 🎉

### Open Slack

Go to any channel or DM

### Type the Command

```
/trade AAPL
```

### You Should See:

✅ A modal (form) pops up!  
✅ Fill it in and click "Execute Trade"  
✅ See a success message with trade details!

---

## ✅ Success Checklist

- [ ] Render service deployed
- [ ] Logs show "✅ OMS API is reachable"
- [ ] Bot URL copied: `https://slackoms-bot.onrender.com`
- [ ] Slash command URL updated in Slack
- [ ] Interactivity URL updated in Slack
- [ ] `/trade` command works in Slack!

---

## 🚨 Troubleshooting

### Still getting "dispatch_failed"

**Cause**: Bot not deployed yet OR wrong URL in Slack  
**Fix**: 
1. Check Render shows "Active" status
2. Check logs in Render for errors
3. Verify URLs in Slack match exactly: `https://slackoms-bot.onrender.com/slack/commands`

### "Invalid signature" error

**Cause**: Wrong Signing Secret  
**Fix**: Double-check `SLACK_SIGNING_SECRET` in Render matches the one from Slack API Dashboard → Basic Information

### Modal doesn't appear

**Cause**: Interactivity URL not set correctly  
**Fix**: Make sure it's `https://slackoms-bot.onrender.com/slack/interactions` (with `/slack/interactions` at the end!)

### "OMS API not reachable" in logs

**Cause**: OMS API is sleeping or wrong API key  
**Fix**: 
1. Wake up OMS API: `curl https://slackoms-api.onrender.com/health`
2. Verify `OMS_API_KEY` in Render matches your key

---

## 🎯 Quick Command Reference

After deployment, test these:

```bash
# Test bot health
curl https://slackoms-bot.onrender.com/health

# Test OMS API
curl https://slackoms-api.onrender.com/health
```

Both should return 200 OK!

---

## 📞 Need Help?

If you get stuck, check:
1. Render logs (Dashboard → slackoms-bot → Logs)
2. Make sure Root Directory is `slack-bot` not empty!
3. All 5 environment variables are set
4. Both URLs in Slack are updated

---

**Ready?** Open **https://dashboard.render.com** and let's deploy! 🚀

