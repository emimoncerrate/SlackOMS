# Troubleshooting: /trade Command Not Showing in Slack

## Symptom:
You type `/trade AAPL` in Slack and **nothing happens** - no response, no error, no dispatch_failed message.

---

## 🎯 Root Cause Analysis

If Slack doesn't respond AT ALL, it means one of these:

1. ❌ Slash command not created in Slack App
2. ❌ App not installed to workspace
3. ❌ Bot not invited to the channel
4. ❌ Command not saved properly

---

## ✅ Step-by-Step Fix

### Step 1: Verify Slash Command Exists

1. Go to: https://api.slack.com/apps
2. Click on your **"Paper Trading Bot"** app
3. Click **"Slash Commands"** (left sidebar)

**What you should see:**
```
Command: /trade
Request URL: [some URL]
Short Description: Execute a paper trade
```

**If you DON'T see `/trade` listed:**
- Click **"Create New Command"**
- Command: `/trade`
- Request URL: `https://TEMP.com` (we'll fix this later)
- Short Description: `Execute a paper trade`
- Usage Hint: `[TICKER] [QUANTITY]`
- Click **"Save"**

---

### Step 2: Check if App is Installed

1. Still on https://api.slack.com/apps
2. Your app → **"Install App"** (left sidebar)

**Look for:**
```
✅ Installed to [Your Workspace Name]
   Bot User OAuth Token: xoxb-...
```

**If you see "Not Installed" or "Install to Workspace":**
- Click **"Install to Workspace"** or **"Reinstall App"**
- Click **"Allow"** when prompted
- This gives your bot permission to work

---

### Step 3: Verify in Slack Directly

**Test if Slack knows about the command:**

1. Open Slack
2. In **any channel or DM**, type: `/`
3. You should see a list of available commands
4. Start typing `/tra...`

**Expected Result:**
```
/trade
Execute a paper trade
```

**If you DON'T see `/trade` in the list:**
→ The command isn't properly installed (go back to Step 2)

---

### Step 4: Check Bot is in Channel (if using a channel)

If you're typing in a **channel** (not a DM):

1. Look at the channel members list (click channel name → Members tab)
2. Search for your bot name (e.g., "Paper Trading Bot")

**If bot is NOT in the channel:**
- Type in the channel: `/invite @Paper Trading Bot`
- Or: Click "Add people" → Search for your bot → Add

**Note:** Slash commands usually work WITHOUT the bot being in the channel, but some workspace settings require it.

---

### Step 5: Get Your Bot Service URL from Render

Now we need to connect Slack to your deployed bot:

1. Go to: https://dashboard.render.com
2. Find your **Slack Bot service**
3. Copy the URL at the top (e.g., `https://[service-name].onrender.com`)

---

### Step 6: Update Slash Command URL

1. Back to: https://api.slack.com/apps → Your App → **"Slash Commands"**
2. Click on **`/trade`** to edit it
3. **Request URL**: Change from `TEMP.com` to:
   ```
   https://[your-bot-url].onrender.com/slack/commands
   ```
   Example: `https://slackoms-bot.onrender.com/slack/commands`
4. Click **"Save"**

---

### Step 7: Update Interactivity URL

1. Same app → **"Interactivity & Shortcuts"** (left sidebar)
2. Make sure **"Interactivity"** is **ON**
3. **Request URL**: Set to:
   ```
   https://[your-bot-url].onrender.com/slack/interactions
   ```
4. Click **"Save Changes"**

---

### Step 8: Reinstall App (IMPORTANT!)

After changing URLs, you MUST reinstall:

1. Go to **"Install App"** (left sidebar)
2. Click **"Reinstall App"** button
3. Click **"Allow"**

This refreshes Slack's knowledge of your app!

---

## 🧪 Test Again

1. Open Slack
2. In any channel or DM, type: `/trade AAPL`
3. Press Enter

**Expected Result:**
- 🔄 **"dispatch_failed"** → Bot URL is wrong or bot is down
- ✅ **Modal pops up** → IT WORKS! 🎉

---

## 🆘 Still Not Working? Check These:

### Check 1: Is Bot Service Running on Render?

```bash
curl https://[your-bot-url].onrender.com/health
```

Should return:
```json
{
  "status": "healthy",
  "service": "SlackOMS Bot",
  "oms_api_connected": true
}
```

If this fails → Your bot isn't deployed or is sleeping (free tier sleeps after 15 min)

### Check 2: Wake Up Sleeping Service

If bot is asleep on Render:
```bash
# This will wake it up
curl https://[your-bot-url].onrender.com/health
```
Wait 30-60 seconds, then try `/trade` again in Slack.

### Check 3: Check Render Logs

1. Go to Render Dashboard → Your bot service
2. Click **"Logs"** tab
3. Look for errors when you type `/trade` in Slack

You should see:
```
INFO: 127.0.0.1 - "POST /slack/commands HTTP/1.1" 200 OK
```

If you see nothing → Slack isn't reaching your bot (wrong URL)

---

## 📋 Quick Checklist

- [ ] `/trade` command exists in Slack App settings
- [ ] App is installed to workspace
- [ ] Bot service is deployed and running on Render
- [ ] Bot service health check returns 200 OK
- [ ] Slash command URL points to: `https://[bot-url]/slack/commands`
- [ ] Interactivity URL points to: `https://[bot-url]/slack/interactions`
- [ ] App was reinstalled after changing URLs
- [ ] Tested `/trade AAPL` in Slack

---

## 🎯 Most Common Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Nothing happens | Command not installed | Reinstall app in Slack |
| "dispatch_failed" | Wrong URL or bot down | Fix URL, wake up bot |
| "Invalid signature" | Wrong signing secret | Check env vars in Render |
| Modal doesn't appear | Interactivity URL wrong | Update and reinstall |

---

## 📝 What to Tell Me

To help you further, tell me:
1. Do you see `/trade` when you type `/` in Slack?
2. What's your bot service URL on Render?
3. Is the bot service showing "Deploy live" on Render?
4. What happens when you run: `curl https://[bot-url]/health`?

Let's get this working! 🚀


