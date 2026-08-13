import requests
import json

# Test the crop recommendation endpoint
test_data = {
    'nitrogen': 45,
    'phosphorus': 25,
    'potassium': 80,
    'ph': 6.5,
    'moisture': 60
}

try:
    response = requests.post('http://localhost:5000/recommend-crop', json=test_data, timeout=10)
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print('✅ Crop recommendation endpoint working!')
        print(f'Top recommendation: {result.get("top_recommendation", "N/A")}')
    else:
        print(f'❌ Error: {response.text}')
except Exception as e:
    print(f'❌ Connection error: {e}')
    print('Make sure backend is running on port 5000')
