import requests
import json

# Test the Crop Recommendation endpoint
url = "http://127.0.0.1:5001/crop-recommend"
data = {
    "nitrogen": 45.0,
    "phosphorus": 35.0,
    "potassium": 50.0,
    "ph": 6.5,
    "temperature": 25.5,
    "humidity": 75.2,
    "soil_moisture": 65.0
}

print("🌱 Testing Crop Recommendation Service...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Success: {result}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
    print("💡 Make sure the Crop Recommendation server is running on port 5001")
    print("   Run: python crop_recommendation.py")
