#!/usr/bin/env python3
"""
Quick test script to verify OpenAI API key is working.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_openai_api():
    """Test the OpenAI API key by making a simple API call."""
    
    # Check if API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("Make sure your .env file contains a valid OPENAI_API_KEY")
        return False
    
    # Mask the key for display (show only first 8 and last 4 characters)
    masked_key = f"{api_key[:8]}...{api_key[-4:]}"
    print(f"🔑 Found API key: {masked_key}")
    
    try:
        # Import OpenAI (this will fail if not installed)
        try:
            from openai import OpenAI
        except ImportError:
            print("❌ ERROR: OpenAI library not installed")
            print("Run: pip install openai")
            return False
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
        
        # Make a simple API call
        print("🧪 Testing API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello! Your OpenAI API key is working correctly.'"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        # Extract and display the response
        message = response.choices[0].message.content.strip()
        print(f"✅ API Response: {message}")
        
        # Check usage information
        if hasattr(response, 'usage'):
            usage = response.usage
            print(f"📊 Token usage - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")
        
        print("\n🎉 SUCCESS: Your OpenAI API key is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: API call failed - {str(e)}")
        
        # Provide specific error guidance
        error_str = str(e).lower()
        if "invalid api key" in error_str or "unauthorized" in error_str:
            print("\n💡 Troubleshooting:")
            print("   - Check that your API key is correct")
            print("   - Verify the key hasn't expired")
            print("   - Ensure you have credits available in your OpenAI account")
        elif "quota" in error_str or "billing" in error_str:
            print("\n💡 Troubleshooting:")
            print("   - You may have exceeded your API quota")
            print("   - Check your OpenAI billing settings")
            print("   - Add payment method if needed")
        elif "rate limit" in error_str:
            print("\n💡 Troubleshooting:")
            print("   - You're hitting rate limits")
            print("   - Wait a moment and try again")
        
        return False

def main():
    """Main function to run the API key test."""
    print("🚀 OpenAI API Key Test")
    print("=" * 40)
    
    success = test_openai_api()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Test completed successfully!")
        sys.exit(0)
    else:
        print("❌ Test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
