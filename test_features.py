#!/usr/bin/env python3
"""
Test script for Wiko Cutlery Chatbot core features
Tests PDF processing, Ollama integration, and other services
"""

import os
import sys
import requests
import json
from io import BytesIO

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_ollama_connection():
    """Test Ollama service connection"""
    print("Testing Ollama connection...")
    try:
        from src.services.ollama_client import OllamaClient
        
        client = OllamaClient()
        is_available = client.is_available()
        
        if is_available:
            print("✅ Ollama service is available")
            
            # List available models
            models = client.list_models()
            print(f"Available models: {[model.get('name', 'Unknown') for model in models]}")
            
            # Test simple generation
            response = client.generate_response(
                model="llama3:8b",  # Try llama3 first
                prompt="Hello, this is a test. Please respond briefly.",
                temperature=0.7
            )
            
            if 'error' not in response:
                print("✅ Ollama generation test successful")
                print(f"Response: {response.get('response', 'No response')[:100]}...")
            else:
                print(f"❌ Ollama generation failed: {response.get('error')}")
                # Try with mistral if llama3 fails
                print("Trying with Mistral model...")
                response = client.generate_response(
                    model="mistral:7b",
                    prompt="Hello, this is a test. Please respond briefly.",
                    temperature=0.7
                )
                if 'error' not in response:
                    print("✅ Mistral generation test successful")
                else:
                    print(f"❌ Both models failed. Error: {response.get('error')}")
        else:
            print("❌ Ollama service is not available")
            print("Please ensure Ollama is running on localhost:11434")
            
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")

def test_pdf_processing():
    """Test PDF processing functionality"""
    print("\nTesting PDF processing...")
    try:
        from src.services.pdf_processor import PDFProcessor
        
        processor = PDFProcessor()
        
        # Create a simple test PDF content
        test_content = """
        WIKO CUTLERY BUSINESS REPORT
        Date: January 15, 2025
        
        Sales Summary:
        - Q4 2024 Revenue: $125,000
        - Customer Complaints: 3
        - New Product Launch: Premium Chef Knife Set
        
        Customer Feedback:
        "Excellent quality knives, very sharp and durable." - customer@email.com
        
        Contact Information:
        Wiko Cutlery Inc.
        Phone: (555) 123-4567
        Email: info@wiko-cutlery.com
        """
        
        # For testing, we'll analyze the text content directly
        business_analysis = processor.analyze_business_content(test_content)
        
        print("✅ PDF text analysis successful")
        print(f"Dates found: {business_analysis['dates']}")
        print(f"Amounts found: {business_analysis['amounts']}")
        print(f"Emails found: {business_analysis['emails']}")
        print(f"Companies found: {business_analysis['companies']}")
        print(f"Key terms found: {business_analysis['key_terms']}")
        
    except Exception as e:
        print(f"❌ Error testing PDF processing: {e}")

def test_chatbot_service():
    """Test chatbot service functionality"""
    print("\nTesting chatbot service...")
    try:
        from src.services.ollama_client import ChatbotService
        
        chatbot = ChatbotService()
        
        # Test different context types
        test_cases = [
            {
                "message": "Analyze this customer complaint: The knife I bought last week is already dull and the handle feels loose.",
                "context": "complaint_handling",
                "description": "Complaint analysis"
            },
            {
                "message": "Generate a professional email response to a customer asking about our warranty policy.",
                "context": "email_assistance", 
                "description": "Email generation"
            },
            {
                "message": "Translate this to German: Thank you for your purchase. Your order will be shipped within 2 business days.",
                "context": "translation",
                "description": "Translation service"
            }
        ]
        
        for test_case in test_cases:
            print(f"\nTesting {test_case['description']}...")
            response = chatbot.get_response(
                message=test_case["message"],
                context_type=test_case["context"]
            )
            
            if 'error' not in response:
                content = response.get('response', '')
                if 'message' in response:
                    content = response['message']['content']
                print(f"✅ {test_case['description']} successful")
                print(f"Response preview: {content[:150]}...")
            else:
                print(f"❌ {test_case['description']} failed: {response.get('error')}")
                
    except Exception as e:
        print(f"❌ Error testing chatbot service: {e}")

def test_flask_endpoints():
    """Test Flask API endpoints"""
    print("\nTesting Flask API endpoints...")
    
    # Start Flask app in background for testing
    import subprocess
    import time
    import signal
    
    try:
        # Start Flask app
        flask_process = subprocess.Popen(
            ["python", "src/main.py"],
            cwd="/home/ubuntu/wiko_chatbot",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for Flask to start
        time.sleep(3)
        
        base_url = "http://localhost:5000/api"
        
        # Test health endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health endpoint working")
                health_data = response.json()
                print(f"Ollama status: {health_data.get('ollama_available', 'Unknown')}")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Health endpoint error: {e}")
        
        # Test authentication
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=5)
            if response.status_code == 200:
                print("✅ Authentication endpoint working")
            else:
                print(f"❌ Authentication failed: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Authentication error: {e}")
        
    except Exception as e:
        print(f"❌ Error testing Flask endpoints: {e}")
    finally:
        # Clean up Flask process
        try:
            flask_process.terminate()
            flask_process.wait(timeout=5)
        except:
            flask_process.kill()

def main():
    """Run all tests"""
    print("=== Wiko Cutlery Chatbot Feature Tests ===\n")
    
    test_ollama_connection()
    test_pdf_processing()
    test_chatbot_service()
    test_flask_endpoints()
    
    print("\n=== Test Summary ===")
    print("If all tests passed, the core features are working correctly.")
    print("If any tests failed, check the error messages and ensure:")
    print("1. Ollama is running with llama3:8b or mistral:7b model")
    print("2. All Python dependencies are installed")
    print("3. Database is initialized")

if __name__ == "__main__":
    main()

