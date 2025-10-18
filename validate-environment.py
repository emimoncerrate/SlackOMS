#!/usr/bin/env python3
"""
Environment Validation Script for Jain Global Slack Trading Bot

This script validates your environment configuration and tests API connections
before deployment or local development.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from typing import List, Tuple, Dict, Any

# Load environment variables
load_dotenv()

def print_banner():
    """Print validation banner."""
    print("=" * 70)
    print("🔍 Jain Global Slack Trading Bot - Environment Validation")
    print("=" * 70)
    print()

def check_required_env_vars() -> List[str]:
    """Check if all required environment variables are set."""
    required_vars = [
        'SLACK_BOT_TOKEN',
        'SLACK_SIGNING_SECRET',
        'DATABASE_URL',
        'FINNHUB_API_KEY',
        'ALPACA_API_KEY',
        'ALPACA_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

def validate_slack_config() -> Tuple[bool, str]:
    """Validate Slack configuration."""
    bot_token = os.getenv('SLACK_BOT_TOKEN')
    signing_secret = os.getenv('SLACK_SIGNING_SECRET')
    
    if not bot_token:
        return False, "SLACK_BOT_TOKEN is not set"
    
    if not bot_token.startswith('xoxb-'):
        return False, "SLACK_BOT_TOKEN must start with 'xoxb-'"
    
    if not signing_secret:
        return False, "SLACK_SIGNING_SECRET is not set"
    
    if len(signing_secret) < 32:
        return False, "SLACK_SIGNING_SECRET appears to be invalid (too short)"
    
    return True, "Slack configuration is valid"

def validate_database_config() -> Tuple[bool, str]:
    """Validate database configuration."""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        return False, "DATABASE_URL is not set"
    
    if database_url.startswith('sqlite:'):
        return True, "SQLite database configuration is valid"
    
    if not (database_url.startswith('postgresql://') or database_url.startswith('postgres://')):
        return False, "DATABASE_URL must be SQLite or PostgreSQL"
    
    return True, "PostgreSQL database configuration is valid"

def test_finnhub_api() -> Tuple[bool, str]:
    """Test Finnhub API connection."""
    api_key = os.getenv('FINNHUB_API_KEY')
    
    if not api_key:
        return False, "FINNHUB_API_KEY is not set"
    
    try:
        response = requests.get(
            f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={api_key}",
            timeout=10
        )
        
        if response.status_code == 401:
            return False, "Invalid Finnhub API key"
        
        if response.status_code == 429:
            return False, "Finnhub API rate limit exceeded"
        
        if response.status_code != 200:
            return False, f"Finnhub API error: {response.status_code}"
        
        data = response.json()
        if 'c' not in data:
            return False, "Invalid Finnhub API response format"
        
        return True, f"Finnhub API is working (AAPL price: ${data['c']})"
        
    except requests.exceptions.Timeout:
        return False, "Finnhub API request timed out"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Finnhub API"
    except Exception as e:
        return False, f"Finnhub API test failed: {str(e)}"

def test_alpaca_api() -> Tuple[bool, str]:
    """Test Alpaca API connection."""
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key:
        return False, "ALPACA_API_KEY is not set"
    
    if not secret_key:
        return False, "ALPACA_SECRET_KEY is not set"
    
    try:
        # Try to import our custom Alpaca client
        from services.simple_alpaca_client import SimpleAlpacaClient
        
        # Create API instance
        api = SimpleAlpacaClient(
            api_key=api_key, 
            secret_key=secret_key, 
            base_url='https://paper-api.alpaca.markets'
        )
        
        # Test connection by getting account info
        account = api.get_account()
        
        if account:
            return True, f"Alpaca API is working (Account: {account.get('status', 'Unknown')}, Buying Power: ${account.get('buying_power', 0):,.2f})"
        else:
            return False, "Alpaca API returned no account data"
            
    except ImportError:
        return False, "SimpleAlpacaClient not available. Check services/simple_alpaca_client.py"
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "unauthorized" in error_msg.lower():
            return False, "Invalid Alpaca API credentials"
        elif "403" in error_msg or "forbidden" in error_msg.lower():
            return False, "Alpaca API access forbidden - check account status"
        else:
            return False, f"Alpaca API test failed: {error_msg}"

def test_database_connection() -> Tuple[bool, str]:
    """Test database connection."""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        return False, "DATABASE_URL is not set"
    
    try:
        if database_url.startswith('sqlite:'):
            # Test SQLite
            import sqlite3
            # Extract path from sqlite:///path
            db_path = database_url.replace('sqlite:///', '')
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
            
            # Test connection
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            
            return True, f"SQLite database connection successful ({db_path})"
        
        else:
            # Test PostgreSQL
            import psycopg2
            from urllib.parse import urlparse
            
            parsed = urlparse(database_url)
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],  # Remove leading /
                user=parsed.username,
                password=parsed.password
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            
            return True, f"PostgreSQL database connection successful ({parsed.hostname})"
            
    except ImportError as e:
        if 'psycopg2' in str(e):
            return False, "psycopg2 package not installed. Run: pip install psycopg2-binary"
        else:
            return False, f"Database driver not available: {e}"
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"

def validate_optional_config() -> Dict[str, Any]:
    """Validate optional configuration."""
    config_status = {}
    
    # Environment
    environment = os.getenv('ENVIRONMENT', 'development')
    config_status['environment'] = environment
    
    # Port
    try:
        port = int(os.getenv('PORT', '8080'))
        config_status['port'] = f"Valid ({port})"
    except ValueError:
        config_status['port'] = "Invalid (not a number)"
    
    # Log level
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level.upper() in valid_levels:
        config_status['log_level'] = f"Valid ({log_level})"
    else:
        config_status['log_level'] = f"Invalid ({log_level})"
    
    # Debug mode
    debug_mode = os.getenv('DEBUG_MODE', 'false').lower()
    config_status['debug_mode'] = debug_mode in ['true', '1', 'yes']
    
    return config_status

def main():
    """Main validation function."""
    print_banner()
    
    all_passed = True
    
    # Check required environment variables
    print("📋 Checking Required Environment Variables...")
    missing_vars = check_required_env_vars()
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("   Run setup-environment.py to configure your environment")
        all_passed = False
    else:
        print("✅ All required environment variables are set")
    
    print()
    
    # Validate configurations
    validations = [
        ("Slack Configuration", validate_slack_config),
        ("Database Configuration", validate_database_config),
    ]
    
    for name, validator in validations:
        print(f"🔧 Validating {name}...")
        is_valid, message = validator()
        
        if is_valid:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            all_passed = False
        
        print()
    
    # Test API connections
    api_tests = [
        ("Finnhub API", test_finnhub_api),
        ("Alpaca API", test_alpaca_api),
        ("Database Connection", test_database_connection),
    ]
    
    for name, test_func in api_tests:
        print(f"🌐 Testing {name}...")
        is_working, message = test_func()
        
        if is_working:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            all_passed = False
        
        print()
    
    # Validate optional configuration
    print("⚙️  Optional Configuration Status...")
    optional_config = validate_optional_config()
    
    for key, value in optional_config.items():
        print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print()
    
    # Summary
    print("=" * 70)
    if all_passed:
        print("🎉 Environment validation PASSED! Your bot is ready to run.")
        print()
        print("Next steps:")
        print("1. For local development: python app.py")
        print("2. For Render deployment: Follow POSTGRESQL_DEPLOYMENT_GUIDE.md")
    else:
        print("❌ Environment validation FAILED! Please fix the issues above.")
        print()
        print("Common solutions:")
        print("1. Run setup-environment.py to configure missing variables")
        print("2. Check your API keys in the respective dashboards")
        print("3. Verify database connection settings")
    
    print("=" * 70)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nValidation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)