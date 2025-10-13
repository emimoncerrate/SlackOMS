# Deployment Guide - OMS API to Render

This guide will walk you through deploying the OMS API to Render (free tier).

## Prerequisites

- GitHub account
- Render account (sign up at https://render.com)
- Your code pushed to a GitHub repository

## Step 1: Push Code to GitHub

```bash
cd /path/to/SlackOMS
git init
git add .
git commit -m "Initial commit: OMS API"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/SlackOMS.git
git push -u origin main
```

## Step 2: Create PostgreSQL Database on Render

1. Log in to Render Dashboard: https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure database:
   - **Name**: `slackoms-db`
   - **Database**: `slackoms`
   - **User**: `slackoms` (auto-generated)
   - **Region**: Choose closest to you
   - **Plan**: **Free**
4. Click **"Create Database"**
5. Wait for database to be created (2-3 minutes)
6. **Copy the Internal Database URL** (you'll need this)

## Step 3: Create Web Service on Render

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:

### Basic Settings
- **Name**: `slackoms-api`
- **Region**: Same as database
- **Branch**: `main`
- **Root Directory**: `oms-api`
- **Runtime**: `Python 3`

### Build & Deploy
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
  
- **Start Command**:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### Plan
- **Instance Type**: **Free**

## Step 4: Configure Environment Variables

Click on **"Environment"** tab and add these variables:

| Key | Value | Notes |
|-----|-------|-------|
| `OMS_API_KEY` | `your-generated-api-key` | Generate using `python generate_api_key.py` |
| `DATABASE_URL` | Paste the Internal Database URL from Step 2 | Auto-filled if you link the database |
| `ENVIRONMENT` | `production` | |
| `PYTHON_VERSION` | `3.11.0` | Specify Python version |

### To Generate API Key:
```bash
python generate_api_key.py
```
Copy the output and paste it as `OMS_API_KEY`.

## Step 5: Link Database (Optional but Recommended)

In the web service settings:
1. Scroll to **"Environment Variables"**
2. Click **"Add from Database"**
3. Select your `slackoms-db` database
4. This will automatically set `DATABASE_URL`

## Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Initialize the database
   - Start your application
3. Wait for deployment (5-10 minutes for first deploy)
4. You'll get a URL like: `https://slackoms-api.onrender.com`

## Step 7: Verify Deployment

### Test Health Endpoint
```bash
curl https://slackoms-api.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "SlackOMS API",
  "version": "1.0.0",
  "timestamp": "2025-10-13T21:00:00"
}
```

### Test Trade Execution
```bash
curl -X POST https://slackoms-api.onrender.com/api/v1/trade \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "quantity": 100,
    "gmv": 17500.00,
    "side": "BUY",
    "portfolio_name": "Test Portfolio",
    "user_id": "U123"
  }'
```

### View API Documentation
Open in browser: `https://slackoms-api.onrender.com/docs`

## Troubleshooting

### Build Fails
- **Error**: `pg_config executable not found`
  - **Solution**: This is expected on first build. Render will retry automatically.
  - Make sure `psycopg2-binary` is in `requirements.txt`

### Database Connection Error
- **Error**: `could not connect to server`
  - **Solution**: Make sure `DATABASE_URL` is set correctly
  - Verify database is in the same region as the web service

### Application Won't Start
- **Error**: `ValidationError: OMS_API_KEY field required`
  - **Solution**: Make sure all environment variables are set
  - Check for typos in variable names

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- First request after inactivity takes ~30 seconds (cold start)
- PostgreSQL database limited to 1GB storage
- 750 hours/month of runtime (sufficient for testing)

## Post-Deployment

### Save Your URLs
Create a file with your deployment URLs:

```bash
cat > deployment_urls.txt << EOF
OMS API URL: https://slackoms-api.onrender.com
API Documentation: https://slackoms-api.onrender.com/docs
Health Check: https://slackoms-api.onrender.com/health
Database: (internal URL - keep secret)
EOF
```

### Update .env for Local Development
Your local `.env` should point to local database:
```env
OMS_API_KEY=your-local-key
DATABASE_URL=sqlite:///./slackoms.db
```

### Monitor Your Application
- Render Dashboard shows:
  - Deployment logs
  - Runtime logs
  - Metrics (CPU, Memory)
  - Health checks

## Next Steps

Once your OMS API is deployed:
1. ✅ Test all endpoints using Postman or curl
2. ✅ Save the API URL and API key securely
3. ➡️ Proceed to Phase 2: Build Slack Bot
4. ➡️ Configure Slack Bot to call your deployed OMS API

## Security Recommendations

1. **Never commit `.env` files** - they're in `.gitignore`
2. **Rotate API keys regularly** - generate new ones monthly
3. **Use HTTPS only** - Render provides this automatically
4. **Monitor logs** - check for suspicious activity
5. **Keep dependencies updated** - run `pip list --outdated`

## Costs

- **Current Setup**: $0/month (Free tier)
- **If you need more**: Starter plan ($7/month) removes spin-down

---

**Need Help?**
- Render Documentation: https://render.com/docs
- Check Render logs in dashboard
- Review `SETUP_GUIDE.md` for local debugging

