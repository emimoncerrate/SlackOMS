#!/usr/bin/env python3
"""
Generate a secure API key for OMS API
Run this script to create a new API key
"""
import secrets

def generate_api_key(length: int = 32) -> str:
    """Generate a cryptographically secure API key"""
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    api_key = generate_api_key()
    print("=" * 60)
    print("Generated API Key (save this securely!):")
    print("=" * 60)
    print(f"\n{api_key}\n")
    print("=" * 60)
    print("\nAdd this to your .env file:")
    print(f"OMS_API_KEY={api_key}")
    print("=" * 60)

