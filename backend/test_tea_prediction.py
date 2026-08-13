import requests
import json

# Test the Tea Prediction endpoint
url = "http://127.0.0.1:5002/tea-predict"
data = {
    "temperature": 25.5,
    "humidity": 75.2,
    "rainfall": 150.0,
    "nitrogen": 45.0,
    "phosphorus": 35.0,
    "potassium": 50.0,
    "ph": 6.5,
    "soil_moisture": 65.0,
    "wind_speed": 12.5,
    "sunlight_hours": 8.0,
    "altitude": 1200.0,
    "latitude": 12.97,
    "longitude": 77.59,
    "soil_type": 2.0,
    "season": 1.0,
    "fertilizer_used": 1.0,
    "irrigation": 1.0
}

print("🍵 Testing Tea Prediction Service...")
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
    print("💡 Make sure the Tea Prediction server is running on port 5002")
    print("   Run: python tea_prediction.py")
