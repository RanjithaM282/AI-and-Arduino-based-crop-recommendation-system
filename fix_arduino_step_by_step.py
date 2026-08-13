#!/usr/bin/env python3
"""
Step-by-Step Arduino Connection Fix
Follow these instructions exactly to get real Arduino data
"""

import serial
import json
import time
import requests

def check_arduino_status():
    """Check current Arduino connection status"""
    print("Current Arduino Connection Status")
    print("=" * 40)
    
    try:
        # Check if we can connect to COM3
        arduino_port = serial.Serial('COM3', 9600, timeout=2)
        print("COM3 Status: Available")
        arduino_port.close()
    except serial.SerialException as e:
        print(f"COM3 Status: {e}")
        print("This means another program is using COM3")
        print("Most likely: Arduino IDE Serial Monitor is OPEN")
    
    # Check backend sensor status
    try:
        response = requests.get('http://localhost:5000/sensor', timeout=2)
        if response.status_code == 200:
            sensor_data = response.json()
            print(f"Backend Arduino Status: {sensor_data.get('arduino_connected', False)}")
            print(f"Current Sensor Data: {sensor_data.get('sensor_data', {})}")
        else:
            print("Backend Status: Not responding")
    except:
        print("Backend Status: Not running")

def show_fix_steps():
    """Show exact steps to fix Arduino connection"""
    print("\nExact Steps to Fix Arduino Connection")
    print("=" * 50)
    
    print("STEP 1: Close Arduino IDE")
    print("   - Close Arduino IDE completely")
    print("   - Especially close the Serial Monitor window")
    print("   - Only one program can use COM3 at a time")
    
    print("\nSTEP 2: Upload Arduino Code")
    print("   - Open Arduino IDE")
    print("   - Load: hardware/arduino_json_code.ino")
    print("   - Upload to Arduino")
    print("   - CLOSE Serial Monitor immediately after upload")
    
    print("\nSTEP 3: Restart Backend")
    print("   - Stop current backend (Ctrl+C)")
    print("   - Run: python start_backend.py")
    print("   - Look for 'Arduino connected on COM3' message")
    
    print("\nSTEP 4: Test Connection")
    print("   - Run: python fix_arduino_step_by_step.py")
    print("   - Check if real Arduino data appears")
    
    print("\nSTEP 5: Check Frontend")
    print("   - Open frontend: http://localhost:3000")
    print("   - Go to Crop Recommendation")
    print("   - Check if sensor values update from 25°C/60%/50% to real values")

def test_arduino_after_fix():
    """Test Arduino after following the fix steps"""
    print("\nTesting Arduino Connection")
    print("=" * 30)
    
    try:
        # Try to read Arduino data
        arduino_port = serial.Serial('COM3', 9600, timeout=3)
        print("Connected to Arduino!")
        
        # Read for 10 seconds
        for i in range(10):
            if arduino_port.in_waiting > 0:
                line = arduino_port.readline().decode('utf-8').strip()
                if line:
                    print(f"Arduino: {line}")
                    try:
                        data = json.loads(line)
                        print(f"Real Data: Temp={data.get('temp')}°C, Hum={data.get('hum')}%, Soil={data.get('soil')}%")
                        return True
                    except:
                        print(f"Not JSON: {line}")
            time.sleep(1)
        
        print("No data received from Arduino")
        arduino_port.close()
        return False
        
    except serial.SerialException as e:
        print(f"Still cannot connect: {e}")
        return False

if __name__ == "__main__":
    print("Arduino Connection Fix Tool")
    print("=" * 40)
    
    # Check current status
    check_arduino_status()
    
    # Show fix steps
    show_fix_steps()
    
    # Test after fix
    print("\nAfter following the steps above, run this again to test:")
    print("python fix_arduino_step_by_step.py")
