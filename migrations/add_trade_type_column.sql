-- Migration: Add missing trade_type column to trades table
-- Date: 2025-10-18
-- Description: Fixes "column trade_type does not exist" error

-- Add trade_type column if it doesn't exist
ALTER TABLE trades 
ADD COLUMN IF NOT EXISTS trade_type VARCHAR(10) NOT NULL DEFAULT 'buy';

-- Update the column to remove the default after adding it
ALTER TABLE trades 
ALTER COLUMN trade_type DROP DEFAULT;

-- Add comment for documentation
COMMENT ON COLUMN trades.trade_type IS 'Trade action: buy or sell';


