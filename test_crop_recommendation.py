#!/usr/bin/env python3
"""
Test script for the crop recommendation endpoint
"""
import requests
import json

def test_crop_recommendation():
    """Test the crop recommendation endpoint with sample data"""
    
    # Test data for crop recommendation
    test_data = {
        'nitrogen': 45,
        'phosphorus': 25,
        'potassium': 80,
        'ph': 6.5,
        'moisture': 60
    }
    
    try:
        print("🧪 Testing crop recommendation endpoint...")
        print(f"📊 Test data: {test_data}")
        
        # Test the endpoint
        response = requests.post('http://localhost:5000/recommend-crop', 
                               json=test_data, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Crop recommendation endpoint working!")
            print(f"🌾 Top recommendation: {result.get('top_recommendation', 'N/A')}")
            print(f"📈 ML Prediction: {result.get('ml_prediction', 'N/A')}")
            
            # Show top 3 recommendations
            crops = result.get('crop_recommendations', [])
            print("\n🏆 Top 3 Crop Recommendations:")
            for i, crop in enumerate(crops[:3], 1):
                print(f"{i}. {crop['name']} - Score: {crop['score']:.2f} ({crop['suitability']})")
            
            # Show soil analysis
            soil = result.get('soil_analysis', {})
            print(f"\n🌱 Soil Analysis:")
            print(f"   Nitrogen: {soil.get('nitrogen_mg_kg', 'N/A')} mg/kg")
            print(f"   Phosphorus: {soil.get('phosphorus_mg_kg', 'N/A')} mg/kg")
            print(f"   Potassium: {soil.get('potassium_mg_kg', 'N/A')} mg/kg")
            print(f"   pH: {soil.get('ph_value', 'N/A')}")
            print(f"   Moisture: {soil.get('moisture_percent', 'N/A')}%")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the backend server is running on port 5000")
        print("Run: python start_backend.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == '__main__':
    test_crop_recommendation()
