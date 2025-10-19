#!/usr/bin/env python3
"""
Run database migrations for PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def run_migration():
    """Run the trade_type column migration."""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    
    # Handle Render's postgres:// vs postgresql:// URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"🔗 Connecting to database...")
    
    try:
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            print("✅ Connected to database")
            
            # Read and execute migration
            with open('migrations/add_trade_type_column.sql', 'r') as f:
                sql = f.read()
            
            print("📝 Running migration: add_trade_type_column.sql")
            
            # Execute each statement
            for statement in sql.split(';'):
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    connection.execute(text(statement))
                    connection.commit()
            
            print("✅ Migration completed successfully!")
            print()
            print("The 'trade_type' column has been added to the trades table.")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()


