# OMS API - Quick Setup Guide

Follow these steps to get your OMS API running locally.

## Prerequisites

- Python 3.9 or higher
- PostgreSQL installed (or use SQLite for testing)
- Terminal/Command Line access

## Step 1: Install PostgreSQL (if not installed)

### macOS:
```bash
brew install postgresql@14
brew services start postgresql@14
```

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Windows:
Download from: https://www.postgresql.org/download/windows/

## Step 2: Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE slackoms;
CREATE USER slackoms WITH PASSWORD 'your_password_here';
GRANT ALL PRIVILEGES ON DATABASE slackoms TO slackoms;

# Exit psql
\q
```

## Step 3: Generate API Key

```bash
cd oms-api
python3 generate_api_key.py
```

Copy the generated API key - you'll need it in the next step!

## Step 4: Create Environment File

Create a file named `.env` in the `oms-api` directory:

```bash
# Copy from template
cp .env.template .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

Fill in your values:
```env
OMS_API_KEY=your-generated-api-key-from-step-3
DATABASE_URL=postgresql://slackoms:your_password_here@localhost:5432/slackoms
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
RATE_LIMIT_PER_MINUTE=60
```

**Alternative: Use SQLite for Quick Testing**
```env
DATABASE_URL=sqlite:///./slackoms.db
```

## Step 5: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 6: Start the Server

### Option A: Using the run script (recommended)
```bash
./run.sh
```

### Option B: Manually
```bash
# Make sure venv is activated
source venv/bin/activate

# Initialize database
python -c "from app.database import init_db; init_db()"

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 7: Verify It's Working

### Check the health endpoint:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "SlackOMS API",
  "version": "1.0.0",
  "timestamp": "2025-10-13T14:30:00Z"
}
```

### View API documentation:
Open in browser: http://localhost:8000/docs

## Step 8: Run Tests

```bash
# Make sure server is running in another terminal
python test_api.py
```

You should see all tests passing! ✅

## Step 9: Test Trade Execution

### Using curl:
```bash
curl -X POST http://localhost:8000/api/v1/trade \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "quantity": 100,
    "gmv": 17500.00,
    "side": "BUY",
    "portfolio_name": "Tech Portfolio",
    "user_id": "U123TEST"
  }'
```

### Using Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/trade",
    headers={"X-API-Key": "YOUR_API_KEY_HERE"},
    json={
        "symbol": "MSFT",
        "quantity": 50,
        "gmv": 17500.00,
        "side": "BUY",
        "portfolio_name": "Tech Portfolio",
        "user_id": "U123TEST"
    }
)

print(response.json())
```

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.OperationalError: could not connect to server
```
**Solution:** Make sure PostgreSQL is running:
```bash
# macOS
brew services start postgresql@14

# Linux
sudo systemctl start postgresql
```

### Port Already in Use
```
ERROR: [Errno 48] Address already in use
```
**Solution:** Change the port in `.env` or kill the process using port 8000:
```bash
lsof -ti:8000 | xargs kill -9
```

### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:** Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### API Key Issues
If you get 401 Unauthorized errors, verify:
1. You're passing the header: `X-API-Key: your-key`
2. The key in your request matches the one in `.env`
3. There are no extra spaces or newlines in the key

## Next Steps

Once your OMS API is running successfully:

1. **Deploy to Render** (see main README for deployment guide)
2. **Build the Slack Bot** (Phase 2)
3. **Integrate both components**

## Quick Reference

### Start Server
```bash
cd oms-api
./run.sh
```

### Run Tests
```bash
python test_api.py
```

### View Logs
Server logs appear in the terminal where you started the server.

### Stop Server
Press `Ctrl+C` in the terminal running the server.

## Need Help?

- Check the [main README](../README.md)
- View API docs: http://localhost:8000/docs
- Check server logs for detailed error messages

