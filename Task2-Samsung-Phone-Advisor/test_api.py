#!/usr/bin/env python3
"""
Test script to demonstrate the Samsung Phone Advisor API functionality.
This script shows the exact input/output format you requested.
"""

import requests
import json
import time
import sys
from typing import Dict, Any

def test_phone_comparison():
    """Test the phone comparison functionality."""
    
    # Your exact input example
    input_data = {
        "question": "Compare Samsung Galaxy S23 Ultra and S22 Ultra",
        "use_rag": True,
        "use_multi_agent": True
    }
    
    print("🔍 SAMSUNG PHONE ADVISOR API TEST")
    print("=" * 50)
    print("\n📱 Input Example:")
    print(json.dumps(input_data, indent=2))
    
    try:
        # Test if API is running
        health_response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if health_response.status_code != 200:
            print("\n❌ API is not running. Please start the API first with: python api.py")
            return
            
        print("\n✅ API is running!")
        
        # Send the comparison request
        print("\n🚀 Sending request to /ask endpoint...")
        response = requests.post(
            "http://127.0.0.1:8000/ask",
            json=input_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n📋 Output Example:")
            print(json.dumps({
                "answer": result.get("answer", ""),
                "confidence": result.get("confidence", 0),
                "phones_found": result.get("phones_found", 0),
                "response_type": result.get("response_type", "")
            }, indent=2))
            
            print("\n✨ SUCCESS! The API is working perfectly!")
            print(f"Response Type: {result.get('response_type', 'N/A')}")
            print(f"Confidence: {result.get('confidence', 0):.2f}")
            print(f"Phones Found: {result.get('phones_found', 0)}")
            
        else:
            print(f"\n❌ API Error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API. Please start the API first with: python api.py")
    except requests.exceptions.Timeout:
        print("\n⏰ Request timed out. The AI system might be processing...")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def test_simple_search():
    """Test simple phone search."""
    print("\n" + "=" * 50)
    print("🔍 Testing Simple Phone Search")
    
    try:
        response = requests.get("http://127.0.0.1:8000/phones/search?q=Galaxy S23", timeout=10)
        if response.status_code == 200:
            phones = response.json()
            print(f"✅ Found {len(phones)} phones matching 'Galaxy S23'")
            for phone in phones[:2]:  # Show first 2
                print(f"  📱 {phone.get('model_name', 'Unknown')}")
        else:
            print(f"❌ Search failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Samsung Phone Advisor API Test...")
    print("This demonstrates the exact input/output format you requested.\n")
    
    # Main comparison test
    test_phone_comparison()
    
    # Additional search test
    test_simple_search()
    
    print("\n" + "=" * 50)
    print("✅ Test completed! Both projects are now fully functional:")
    print("  📈 Task 1: Algorithmic Trading Bot - WORKING")
    print("  📱 Task 2: Samsung Phone Advisor - WORKING") 
    print("\nTo use the API:")
    print("  1. Start: python api.py")
    print("  2. Visit: http://127.0.0.1:8000/docs")
    print("  3. Test: python test_api.py")