#!/usr/bin/env python3
"""
Quick API quota check script for Google Gemini API.
Run this before using the main agent to check if your API quota is available.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

def check_api_quota():
    """Check if Google Gemini API is available and has quota."""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    try:
        # Initialize Gemini with minimal configuration
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            api_key=api_key,
            timeout=10
        )
        
        # Try a very simple test call
        test_message = HumanMessage(content="Reply with just 'OK'")
        response = llm.invoke([test_message])
        
        if response and response.content:
            print("✅ Google Gemini API is working!")
            print(f"   Response: {response.content.strip()}")
            return True
        else:
            print("❌ API responded but with empty content")
            return False
            
    except Exception as e:
        error_str = str(e)
        if "quota" in error_str.lower() or "429" in error_str or "resourceexhausted" in error_str.lower():
            print("❌ Google Gemini API quota exceeded!")
            print("   Free tier limit: 50 requests per day")
            print("   Solutions:")
            print("   • Wait 24 hours for quota reset")
            print("   • Get a new API key from https://ai.google.dev/")
            print("   • Upgrade to a paid plan")
        elif "api_key" in error_str.lower() or "invalid" in error_str.lower():
            print("❌ Invalid API key!")
            print("   • Check your GEMINI_API_KEY in .env file")
            print("   • Get a new key from https://ai.google.dev/")
        else:
            print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Google Gemini API availability...")
    print()
    success = check_api_quota()
    print()
    
    if success:
        print("🚀 You can now run: python main.py --executive \"Your problem here\"")
    else:
        print("⏳ Please fix the API issue before running the agent")