"""
Test Arduino Connection Script
Checks if Arduino is properly connected and sending data
"""

import serial
import json
import time

def test_arduino_connection():
    """Test Arduino connection on COM3"""
    print("Testing Arduino Connection...")
    print("=" * 40)
    
    try:
        # Try to connect to Arduino on COM3
        print("1. Connecting to Arduino on COM3...")
        arduino_port = serial.Serial('COM3', 9600, timeout=2)
        print("   Connected to Arduino!")
        
        print("2. Waiting for Arduino data...")
        print("   Make sure Arduino is uploading JSON data...")
        
        # Read data for 10 seconds
        for i in range(10):
            if arduino_port.in_waiting > 0:
                line = arduino_port.readline().decode('utf-8').strip()
                if line:
                    print(f"   Received: {line}")
                    try:
                        data = json.loads(line)
                        print(f"   Parsed JSON: {data}")
                        print(f"   Temperature: {data.get('temp')}°C")
                        print(f"   Humidity: {data.get('hum')}%")
                        print(f"   Soil Moisture: {data.get('soil')}%")
                        print("   Arduino working correctly!")
                        break
                    except json.JSONDecodeError:
                        print(f"   Not JSON format: {line}")
            else:
                print(f"   No data received (attempt {i+1}/10)")
            time.sleep(1)
        
        arduino_port.close()
        
    except serial.SerialException as e:
        print(f"   Connection Error: {e}")
        print("   Possible issues:")
        print("   - Arduino not connected to COM3")
        print("   - Arduino not uploading code")
        print("   - Serial Monitor in Arduino IDE is open (close it!)")
        print("   - Wrong COM port number")
        
    except Exception as e:
        print(f"   Error: {e}")

def check_com_ports():
    """Check available COM ports"""
    print("\nChecking Available COM Ports...")
    print("=" * 40)
    
    import serial.tools.list_ports
    
    ports = serial.tools.list_ports.comports()
    if ports:
        print("Available COM ports:")
        for port in ports:
            print(f"   {port.device}: {port.description}")
    else:
        print("No COM ports found!")

if __name__ == "__main__":
    print("Arduino Connection Troubleshooting")
    print("=" * 50)
    
    # Check available COM ports
    check_com_ports()
    
    print("\n")
    
    # Test Arduino connection
    test_arduino_connection()
    
    print("\nTroubleshooting Steps:")
    print("1. Make sure Arduino is connected via USB")
    print("2. Upload the Arduino code (arduino_json_code.ino)")
    print("3. Close Arduino IDE Serial Monitor")
    print("4. Check that DHT11 is on pin 2")
    print("5. Check that soil moisture sensor is on A0")
    print("6. Verify Arduino is sending JSON data")
