#!/usr/bin/env python3
"""
Test Real Arduino Data in Frontend
Check if real Arduino data is appearing
"""

import requests

def test_real_arduino_data():
    """Test if real Arduino data is in frontend"""
    print("Testing Real Arduino Data in Frontend")
    print("=" * 50)
    
    try:
        response = requests.get('http://localhost:5000/sensor', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            sensor_data = data.get('sensor_data', {})
            
            print("Current Arduino Sensor Data:")
            print(f"🌡️ Temperature: {sensor_data.get('temperature', 'N/A')}°C")
            print(f"💧 Humidity: {sensor_data.get('humidity', 'N/A')}%")
            print(f"🌱 Soil Moisture: {sensor_data.get('soil_moisture', 'N/A')}%")
            print(f"🔗 Arduino Connected: {data.get('arduino_connected', False)}")
            print(f"⏰ Timestamp: {sensor_data.get('timestamp', 'Never')}")
            
            # Check if real data
            temp = sensor_data.get('temperature', 0)
            hum = sensor_data.get('humidity', 0)
            soil = sensor_data.get('soil_moisture', 0)
            
            if temp == 25.0 and hum == 60.0 and soil == 50.0:
                print("\n❌ Still showing DEFAULT values!")
                print("Arduino connection not working properly")
            else:
                print("\n✅ Real Arduino data detected!")
                print("Frontend should show your actual sensor readings")
                
        else:
            print(f"❌ Backend error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_real_arduino_data()
