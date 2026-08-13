#!/usr/bin/env python3
"""
Test varied crop recommendations with different soil conditions
"""

import requests

def test_varied_recommendations():
    """Test crop recommendations with different soil conditions"""
    print("Testing Varied Crop Recommendations")
    print("=" * 50)
    
    test_cases = [
        {'nitrogen': 80, 'phosphorus': 60, 'potassium': 120, 'ph': 7.2, 'name': 'High Fertility Soil'},
        {'nitrogen': 20, 'phosphorus': 15, 'potassium': 30, 'ph': 5.8, 'name': 'Low Fertility Soil'},
        {'nitrogen': 50, 'phosphorus': 35, 'potassium': 80, 'ph': 6.8, 'name': 'Balanced Soil'},
        {'nitrogen': 40, 'phosphorus': 25, 'potassium': 80, 'ph': 6.5, 'name': 'Original Test Soil'}
    ]
    
    for test in test_cases:
        try:
            response = requests.post('http://localhost:5000/recommend-crop-with-arduino', json=test, timeout=5)
            if response.status_code == 200:
                result = response.json()
                top_crop = result.get('top_recommendation', 'N/A')
                top_score = result.get('crop_recommendations', [{}])[0].get('score', 0)
                print(f'{test["name"]}: {top_crop} ({top_score:.2f})')
                
                # Show top 3 recommendations
                crops = result.get('crop_recommendations', [])
                print(f'  Top 3: {crops[0]["name"]} ({crops[0]["score"]:.2f}), {crops[1]["name"]} ({crops[1]["score"]:.2f}), {crops[2]["name"]} ({crops[2]["score"]:.2f})')
            else:
                print(f'{test["name"]}: Error {response.status_code}')
        except Exception as e:
            print(f'{test["name"]}: {e}')
        print()

if __name__ == "__main__":
    test_varied_recommendations()
