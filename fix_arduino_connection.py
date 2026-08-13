#!/usr/bin/env python3
"""
Fix Arduino Connection Issues
Check real Arduino data and fix connection problems
"""

import serial
import json
import time
import requests

def check_arduino_real_data():
    """Check what Arduino is actually sending"""
    print("Checking Arduino Real Data...")
    print("=" * 50)
    
    try:
        # Try to connect to Arduino
        print("1. Connecting to Arduino on COM3...")
        arduino_port = serial.Serial('COM3', 9600, timeout=3)
        print("   Connected to Arduino!")
        
        print("2. Reading Arduino data for 10 seconds...")
        print("   Make sure Arduino is running the JSON code...")
        
        real_data_count = 0
        for i in range(20):  # Try for 20 iterations (40 seconds)
            if arduino_port.in_waiting > 0:
                line = arduino_port.readline().decode('utf-8').strip()
                if line:
                    print(f"   Raw Arduino: {line}")
                    real_data_count += 1
                    
                    try:
                        data = json.loads(line)
                        print(f"   Parsed JSON: {data}")
                        print(f"   Temperature: {data.get('temp')}°C")
                        print(f"   Humidity: {data.get('hum')}%")
                        print(f"   Soil Moisture: {data.get('soil')}%")
                        print("   Arduino sending real data!")
                        
                        # Test if this data reaches the backend
                        test_backend_with_real_data(data)
                        break
                        
                    except json.JSONDecodeError:
                        print(f"   Not JSON format: {line}")
            else:
                print(f"   No data (attempt {i+1}/20)")
            
            time.sleep(2)
        
        if real_data_count == 0:
            print("   No real data received from Arduino!")
            print("   Possible issues:")
            print("   - Arduino not running the JSON code")
            print("   - DHT11 sensor not connected properly")
            print("   - Soil moisture sensor not connected")
            print("   - Arduino code needs to be uploaded")
        
        arduino_port.close()
        
    except serial.SerialException as e:
        print(f"   Connection Error: {e}")
        print("   This means:")
        print("   - Arduino IDE Serial Monitor is open (CLOSE IT!)")
        print("   - Another program is using COM3")
        print("   - Arduino not connected")
        
    except Exception as e:
        print(f"   Error: {e}")

def test_backend_with_real_data(arduino_data):
    """Test if backend receives real Arduino data"""
    print("\n3. Testing backend with real Arduino data...")
    
    try:
        # Get current sensor data from backend
        response = requests.get('http://localhost:5000/sensor', timeout=5)
        
        if response.status_code == 200:
            sensor_data = response.json()
            print(f"   Backend sensors: {sensor_data.get('sensor_data', {})}")
            print(f"   Arduino connected: {sensor_data.get('arduino_connected', False)}")
            
            # Compare with real Arduino data
            backend_data = sensor_data.get('sensor_data', {})
            if (backend_data.get('temperature') == arduino_data.get('temp') and
                backend_data.get('humidity') == arduino_data.get('hum') and
                backend_data.get('soil_moisture') == arduino_data.get('soil')):
                print("   Real Arduino data is reaching the backend!")
            else:
                print("   Backend is using default values, not real Arduino data!")
        else:
            print(f"   Backend error: {response.status_code}")
            
    except Exception as e:
        print(f"   Backend test error: {e}")

def suggest_fixes():
    """Suggest specific fixes for Arduino connection"""
    print("\n4. Suggested Fixes:")
    print("=" * 50)
    
    print("Step 1: Upload Arduino Code")
    print("   - Open Arduino IDE")
    print("   - Load 'arduino_json_code.ino'")
    print("   - Upload to Arduino")
    print("   - CLOSE Serial Monitor!")
    
    print("\nStep 2: Check Sensor Connections")
    print("   - DHT11: Pin 2 (data), 5V, GND")
    print("   - Soil Moisture: A0, 5V, GND")
    print("   - Make sure sensors are powered")
    
    print("\nStep 3: Restart Backend")
    print("   - Stop current backend")
    print("   - Run: python start_backend.py")
    print("   - Check for Arduino connection message")
    
    print("\nStep 4: Test Again")
    print("   - Run: python fix_arduino_connection.py")
    print("   - Check if real data appears")

if __name__ == "__main__":
    print("Arduino Connection Fix Tool")
    print("=" * 50)
    
    # Check Arduino real data
    check_arduino_real_data()
    
    # Suggest fixes
    suggest_fixes()
    
    print("\nRemember: CLOSE Arduino IDE Serial Monitor!")
