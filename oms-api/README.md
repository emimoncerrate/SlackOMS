# OMS API - Paper Trading Backend

The core backend service for paper trading execution and portfolio management.

## 🎯 Purpose

This is the "brain" and "ledger" of the system. It:
- Authenticates all incoming requests
- Executes simulated trades
- Maintains persistent portfolio records
- Provides RESTful API for trade operations

## 🏗️ Architecture

**Tech Stack:**
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Deployment**: Render

## 📋 API Endpoints

### Core Endpoints

#### `POST /api/v1/trade`
Execute a paper trade.

**Headers:**
```
X-API-Key: your-secret-key
```

**Request Body:**
```json
{
  "symbol": "AAPL",
  "quantity": 100,
  "gmv": 17500.00,
  "side": "BUY",
  "portfolio_name": "Tech Portfolio",
  "user_id": "U12345"
}
```

**Response:**
```json
{
  "success": true,
  "trade_id": "T1697234567123",
  "message": "Trade executed successfully",
  "trade": {
    "symbol": "AAPL",
    "quantity": 100,
    "side": "BUY",
    "gmv": 17500.00,
    "portfolio_name": "Tech Portfolio",
    "timestamp": "2025-10-13T14:30:00Z"
  }
}
```

#### `GET /api/v1/portfolio/{portfolio_name}`
Get portfolio summary.

#### `GET /api/v1/trades`
List all trades (with pagination).

#### `GET /api/v1/trades/{trade_id}`
Get specific trade details.

#### `GET /health`
Health check endpoint.

## 🚀 Local Development Setup

### 1. Install Dependencies

```bash
cd oms-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

**Generate a secure API key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb slackoms

# Run migrations
alembic upgrade head
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs for interactive API documentation.

## 🧪 Testing

### Using Postman/Insomnia

Import the provided collection or manually test:

**Valid Request:**
```bash
curl -X POST http://localhost:8000/api/v1/trade \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "MSFT",
    "quantity": 50,
    "gmv": 17500.00,
    "side": "BUY",
    "portfolio_name": "Main",
    "user_id": "U123"
  }'
```

**Expected Errors:**
- `401 Unauthorized` - Missing or invalid API key
- `400 Bad Request` - Invalid data format
- `422 Unprocessable Entity` - Validation errors

## 📦 Deployment to Render

### 1. Create PostgreSQL Database on Render
- Go to Render Dashboard
- Create new PostgreSQL database
- Copy the Internal Database URL

### 2. Create Web Service
- Connect your GitHub repository
- Select `oms-api` as root directory
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Environment Variables
Set in Render dashboard:
- `OMS_API_KEY`: Your secure API key
- `DATABASE_URL`: PostgreSQL connection string (auto-filled if linked)
- `ENVIRONMENT`: production

### 4. Deploy
Render will automatically deploy on push to main branch.

## 🔒 Security Considerations

1. **API Key Protection**: Never commit real keys to git
2. **Database Security**: Use connection pooling and SSL in production
3. **Rate Limiting**: Configured to prevent abuse
4. **Input Validation**: All inputs validated before processing
5. **Audit Logging**: All trades and auth attempts logged

## 📊 Database Schema

**trades table:**
- `id` (Primary Key, Auto-increment)
- `trade_id` (Unique, VARCHAR)
- `symbol` (VARCHAR)
- `quantity` (INTEGER)
- `gmv` (DECIMAL)
- `side` (ENUM: BUY/SELL)
- `portfolio_name` (VARCHAR)
- `user_id` (VARCHAR)
- `timestamp` (TIMESTAMP)
- `created_at` (TIMESTAMP)

## 🐛 Troubleshooting

**Database Connection Issues:**
```bash
# Test PostgreSQL connection
psql -d slackoms -c "SELECT version();"
```

**Port Already in Use:**
```bash
# Change port in command
uvicorn app.main:app --port 8001
```

**Import Errors:**
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt --upgrade
```

## 📝 API Documentation

Interactive documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

