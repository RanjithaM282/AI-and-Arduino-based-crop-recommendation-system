import requests
import json

print("🧪 Testing New Rule-Based Crop Recommendation System...")

# Test with sample data
test_data = {
    'nitrogen': 50,
    'phosphorus': 35,
    'potassium': 52,
    'ph': 6.5,
    'temperature': 25,
    'humidity': 60,
    'soil_moisture': 50
}

print(f"📊 Test data: {test_data}")

try:
    response = requests.post(
        'http://127.0.0.1:5001/crop-recommend',
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Crop Recommendation Results:")
        print(f"   Model used: {result['model_used']}")
        print(f"   Top recommendation: {result['top_recommendation']}")
        print(f"\n   All crop scores:")
        for crop in result['crop_recommendations']:
            print(f"   - {crop['name']}: {crop['score']:.3f} ({crop['suitability']})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Test failed: {e}")
    print("Make sure the crop recommendation server is running on port 5001")
