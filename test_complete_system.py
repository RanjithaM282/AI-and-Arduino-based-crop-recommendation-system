#!/usr/bin/env python3
"""
Test Complete Arduino Integration System
Test if real Arduino data is working in frontend
"""

import requests
import time

def test_complete_system():
    """Test complete Arduino integration"""
    print("Testing Complete Arduino Integration")
    print("=" * 50)
    
    try:
        # Test 1: Backend Health
        print("1. Testing Backend Health...")
        health = requests.get('http://localhost:5000/health', timeout=3)
        if health.status_code == 200:
            print("   Backend is healthy")
        else:
            print(f"   Backend error: {health.status_code}")
        
        time.sleep(1)
        
        # Test 2: Arduino Sensor Data
        print("2. Testing Arduino Sensor Data...")
        sensor = requests.get('http://localhost:5000/sensor', timeout=3)
        if sensor.status_code == 200:
            data = sensor.json()
            sensor_data = data.get('sensor_data', {})
            arduino_connected = data.get('arduino_connected', False)
            
            print(f"   Arduino Connected: {arduino_connected}")
            print(f"   Temperature: {sensor_data.get('temperature', 'N/A')}°C")
            print(f"   Humidity: {sensor_data.get('humidity', 'N/A')}%")
            print(f"   Soil Moisture: {sensor_data.get('soil_moisture', 'N/A')}%")
            
            # Check if real data
            temp = sensor_data.get('temperature', 0)
            hum = sensor_data.get('humidity', 0)
            soil = sensor_data.get('soil_moisture', 0)
            
            if temp == 25.0 and hum == 60.0 and soil == 50.0:
                print("   ❌ Still showing DEFAULT values")
                print("   Arduino connection not working properly")
            else:
                print("   ✅ Real Arduino data detected!")
                print("   Frontend should show your actual sensor readings")
        else:
            print(f"   Sensor endpoint error: {sensor.status_code}")
        
        time.sleep(1)
        
        # Test 3: Crop Recommendation
        print("3. Testing Crop Recommendation...")
        test_data = {'nitrogen': 45, 'phosphorus': 25, 'potassium': 80, 'ph': 6.5}
        crop_rec = requests.post('http://localhost:5000/recommend-crop-with-arduino', json=test_data, timeout=5)
        
        if crop_rec.status_code == 200:
            result = crop_rec.json()
            top_crop = result.get('top_recommendation', 'N/A')
            arduino_sensors = result.get('arduino_sensors', {})
            
            print(f"   Top Recommendation: {top_crop}")
            print(f"   Arduino Temperature: {arduino_sensors.get('temperature_c', 'N/A')}°C")
            print(f"   Arduino Humidity: {arduino_sensors.get('humidity_percent', 'N/A')}%")
            print(f"   Arduino Soil Moisture: {arduino_sensors.get('soil_moisture_percent', 'N/A')}%")
            
            if top_crop == 'Vegetables':
                print("   ✅ System working correctly!")
            else:
                print("   System needs debugging")
        else:
            print(f"   Crop recommendation error: {crop_rec.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_complete_system()
