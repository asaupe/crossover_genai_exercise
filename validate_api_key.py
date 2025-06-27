#!/usr/bin/env python3
"""
Simple OpenAI API key format validator.
"""

import os
import re
from dotenv import load_dotenv

def validate_api_key_format(api_key):
    """Validate the format of an OpenAI API key."""
    
    if not api_key:
        return False, "API key is empty"
    
    # OpenAI API keys should start with 'sk-' and be around 51 characters total
    if not api_key.startswith('sk-'):
        return False, "API key should start with 'sk-'"
    
    # Check length (typical OpenAI keys are around 51 characters)
    if len(api_key) < 45 or len(api_key) > 60:
        return False, f"API key length ({len(api_key)}) seems incorrect (should be ~51 characters)"
    
    # Check for valid characters (alphanumeric and some special chars)
    if not re.match(r'^sk-[A-Za-z0-9\-_]+$', api_key):
        return False, "API key contains invalid characters"
    
    return True, "API key format looks correct"

def main():
    """Main function to validate API key format."""
    print("🔍 OpenAI API Key Format Validator")
    print("=" * 45)
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment")
        return
    
    # Show masked key
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
    print(f"🔑 Checking key: {masked_key}")
    print(f"📏 Length: {len(api_key)} characters")
    
    # Validate format
    is_valid, message = validate_api_key_format(api_key)
    
    if is_valid:
        print(f"✅ {message}")
        print("\n💡 Format looks good! If API calls still fail, check:")
        print("   - Key hasn't expired")
        print("   - You have credits in your OpenAI account")
        print("   - Key has proper permissions")
    else:
        print(f"❌ {message}")
        print("\n💡 To get a valid API key:")
        print("   1. Go to https://platform.openai.com/api-keys")
        print("   2. Create a new secret key")
        print("   3. Copy it and update your .env file")
        print("   4. Make sure it starts with 'sk-'")

if __name__ == "__main__":
    main()
