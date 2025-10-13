# SlackOMS - Paper Trading System

A secure paper trading Order Management System (OMS) integrated with Slack for seamless trade execution.

## 🏗️ Architecture

This project follows a **Secure Proxy Pattern** with three layers:

1. **Slack UI** - User interface for trade commands
2. **Slack Bot Server** - Secure intermediary that routes requests
3. **OMS API** - Core business logic and trade ledger

## 📦 Components

### Component 1: OMS API (Backend)
- **Location**: `/oms-api/`
- **Technology**: Python FastAPI + PostgreSQL
- **Purpose**: Executes trades, maintains ledger, provides secure API
- **Deployment**: Render

### Component 2: Slack Bot (Frontend)
- **Location**: `/slack-bot/`
- **Technology**: Python + Slack Bolt SDK
- **Purpose**: Captures user intent, provides UI, routes to OMS
- **Deployment**: Render

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL
- Slack Workspace (for bot integration)

### Setup Instructions

See individual component READMEs:
- [OMS API Setup](./oms-api/README.md)
- [Slack Bot Setup](./slack-bot/README.md)

## 🔒 Security

- All API calls require authentication via `X-API-Key` header
- Slack requests are verified using signing secrets
- Environment variables store all sensitive credentials
- No secrets in code or version control

## 📊 Features

- **Paper Trade Execution**: Simulated BUY/SELL orders
- **Portfolio Tracking**: Multiple portfolio support
- **Slack Integration**: Execute trades via `/trade` command
- **Audit Trail**: Complete logging of all transactions
- **Real-time Confirmation**: Instant trade confirmation in Slack

## 🏁 Project Status

- [x] **Phase 0**: Project Setup ✅
- [x] **Phase 1**: OMS API Development ✅
  - FastAPI backend with PostgreSQL/SQLite
  - Secure API key authentication
  - Trade execution and portfolio tracking
  - Complete test suite (8/8 passing)
- [x] **Phase 2**: Slack Bot Integration ✅
  - Slash command `/trade`
  - Interactive modal UI
  - Real-time confirmations
  - Secure OMS API integration
- [x] **Phase 3**: Documentation & Production Ready ✅
  - Comprehensive guides
  - Deployment documentation
  - Ready for Render (free tier)

## 🚀 Quick Start

See **[QUICKSTART.md](./QUICKSTART.md)** for a step-by-step guide to get running in minutes!

**TL;DR:**
```bash
# 1. Setup OMS API
cd oms-api
python generate_api_key.py
# Create .env with the key
pip install -r requirements-local.txt
uvicorn app.main:app --port 8001

# 2. Setup Slack Bot
cd ../slack-bot
# Create .env with Slack tokens
pip install -r requirements.txt
python main.py

# 3. Test in Slack
/trade AAPL
```

## 📝 License

MIT License - Built for educational and testing purposes.

