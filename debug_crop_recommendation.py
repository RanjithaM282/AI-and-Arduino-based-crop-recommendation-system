#!/usr/bin/env python3
"""
Debug Crop Recommendation System
Tests the crop recommendation endpoint and identifies issues
"""

import requests
import json

def test_crop_recommendation():
    """Test crop recommendation with sample data"""
    print("Testing Crop Recommendation System")
    print("=" * 50)
    
    # Test data
    test_data = {
        'nitrogen': 45,
        'phosphorus': 25,
        'potassium': 80,
        'ph': 6.5
    }
    
    print(f"Test Data: {test_data}")
    print()
    
    try:
        # Test the endpoint
        print("1. Testing /recommend-crop-with-arduino endpoint...")
        response = requests.post('http://localhost:5000/recommend-crop-with-arduino', 
                               json=test_data, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("   Success! Response received:")
            print(f"   Top recommendation: {result.get('top_recommendation', 'N/A')}")
            print(f"   Number of recommendations: {len(result.get('crop_recommendations', []))}")
            
            # Show all recommendations
            recommendations = result.get('crop_recommendations', [])
            if recommendations:
                print("   All recommendations:")
                for i, crop in enumerate(recommendations):
                    print(f"   {i+1}. {crop.get('name', 'Unknown')} - Score: {crop.get('score', 0):.2f} - {crop.get('suitability', 'Unknown')}")
            
            # Show user input and Arduino sensors
            user_input = result.get('user_input', {})
            arduino_sensors = result.get('arduino_sensors', {})
            
            print(f"   User Input: {user_input}")
            print(f"   Arduino Sensors: {arduino_sensors}")
            
        else:
            print(f"   Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   Connection Error: Backend not running")
        print("   Make sure backend is running on port 5000")
        
    except requests.exceptions.Timeout:
        print("   Timeout Error: Request took too long")
        
    except Exception as e:
        print(f"   Error: {e}")

def test_health_endpoint():
    """Test health endpoint to check backend status"""
    print("2. Testing /health endpoint...")
    
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            print("   Backend Health:")
            print(f"   Status: {health.get('status', 'unknown')}")
            print(f"   Model Loaded: {health.get('model_loaded', False)}")
            print(f"   API Key Configured: {health.get('api_key_configured', False)}")
            print(f"   Arduino Endpoint: {health.get('arduino_endpoint', 'none')}")
        else:
            print(f"   Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"   Health check error: {e}")

def test_arduino_sensors():
    """Test Arduino sensor endpoint"""
    print("3. Testing /sensor endpoint...")
    
    try:
        response = requests.get('http://localhost:5000/sensor', timeout=5)
        
        if response.status_code == 200:
            sensor_data = response.json()
            print("   Arduino Sensors:")
            print(f"   Status: {sensor_data.get('status', 'unknown')}")
            print(f"   Connected: {sensor_data.get('arduino_connected', False)}")
            print(f"   Data: {sensor_data.get('sensor_data', {})}")
        else:
            print(f"   Sensor endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"   Sensor endpoint error: {e}")

if __name__ == "__main__":
    print("Crop Recommendation Debug Tool")
    print("=" * 50)
    print()
    
    # Test health first
    test_health_endpoint()
    print()
    
    # Test Arduino sensors
    test_arduino_sensors()
    print()
    
    # Test crop recommendation
    test_crop_recommendation()
    print()
    
    print("Debug Complete!")
    print("If any test failed, check the backend logs for more details.")
