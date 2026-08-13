"""
ESP32 Tea Crop Monitoring System
Real-time sensor data collection and transmission
"""

import machine
import time
import json
import network
import urequests
from machine import Pin, ADC, I2C
from dht import DHT22
import gps

# Pin Definitions
DHT_PIN = 4
SOIL_MOISTURE_PIN = 34
RAIN_PIN = 2
LIGHT_SDA = 21
LIGHT_SCL = 22
PH_PIN = 32

# WiFi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
API_ENDPOINT = "http://your-server.com/api/sensor-data"

class TeaMonitor:
    def __init__(self):
        self.dht = DHT22(Pin(DHT_PIN))
        self.soil_moisture = ADC(Pin(SOIL_MOISTURE_PIN))
        self.soil_moisture.atten(ADC.ATTN_11DB)  # 0-3.6V range
        
        self.rain_sensor = Pin(RAIN_PIN, Pin.IN, Pin.PULL_UP)
        self.rain_count = 0
        self.rain_sensor.irq(trigger=Pin.IRQ_FALLING, handler=self.rain_callback)
        
        self.i2c = I2C(scl=Pin(LIGHT_SCL), sda=Pin(LIGHT_SDA))
        self.ph_sensor = ADC(Pin(PH_PIN))
        self.ph_sensor.atten(ADC.ATTN_11DB)
        
        self.gps_uart = machine.UART(1, 9600, timeout=1000)
        self.gps = gps.GPS(self.gps_uart)
        
        self.location = {"lat": 0.0, "lng": 0.0}
        self.last_rain_reset = time.time()
        
    def rain_callback(self, pin):
        """Rain gauge interrupt handler"""
        self.rain_count += 1
        
    def read_temperature_humidity(self):
        """Read DHT22 sensor"""
        try:
            self.dht.measure()
            temp = self.dht.temperature()
            humidity = self.dht.humidity()
            return temp, humidity
        except:
            return None, None
            
    def read_soil_moisture(self):
        """Read soil moisture sensor"""
        raw_value = self.soil_moisture.read()
        # Convert to percentage (0-100%)
        moisture_percent = (4095 - raw_value) / 4095 * 100
        return max(0, min(100, moisture_percent))
        
    def read_rainfall(self):
        """Calculate rainfall from tipping bucket"""
        current_time = time.time()
        time_diff = current_time - self.last_rain_reset
        
        # Reset counter every hour
        if time_diff >= 3600:
            rainfall_mm = self.rain_count * 0.279  # 0.279mm per tip
            self.rain_count = 0
            self.last_rain_reset = current_time
            return rainfall_mm
        else:
            return self.rain_count * 0.279
            
    def read_light_intensity(self):
        """Read BH1750 light sensor"""
        try:
            # BH1750 address 0x23
            self.i2c.writeto(0x23, b'\x20')  # One-time high-res mode
            time.sleep(0.2)
            data = self.i2c.readfrom(0x23, 2)
            light_level = (data[0] << 8) | data[1]
            return light_level / 1.2  # Convert to lux
        except:
            return 0
            
    def read_ph(self):
        """Read soil pH sensor"""
        raw_value = self.ph_sensor.read()
        # Convert to pH (calibration needed)
        voltage = raw_value / 4095 * 3.3
        ph_value = 7.0 - (voltage - 2.5) * 2  # Rough conversion
        return max(0, min(14, ph_value))
        
    def read_gps(self):
        """Read GPS location"""
        try:
            sentence = self.gps_uart.readline()
            if sentence and b'$GPGGA' in sentence:
                data = sentence.decode('utf-8').split(',')
                if len(data) >= 6 and data[2] and data[4]:
                    lat = float(data[2][:2]) + float(data[2][2:]) / 60
                    if data[3] == 'S':
                        lat = -lat
                    lng = float(data[4][:3]) + float(data[4][3:]) / 60
                    if data[5] == 'W':
                        lng = -lng
                    self.location = {"lat": lat, "lng": lng}
        except:
            pass
        return self.location
        
    def connect_wifi(self):
        """Connect to WiFi"""
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        while not wlan.isconnected():
            time.sleep(1)
            
        print("WiFi connected:", wlan.ifconfig())
        return wlan.isconnected()
        
    def collect_sensor_data(self):
        """Collect all sensor readings"""
        temp, humidity = self.read_temperature_humidity()
        location = self.read_gps()
        
        data = {
            "timestamp": time.time(),
            "location": location,
            "sensors": {
                "temperature": temp,
                "humidity": humidity,
                "soil_moisture": self.read_soil_moisture(),
                "rainfall": self.read_rainfall(),
                "light_intensity": self.read_light_intensity(),
                "soil_ph": self.read_ph(),
                "battery_level": self.read_battery_level()
            }
        }
        
        return data
        
    def read_battery_level(self):
        """Read battery voltage"""
        # Assuming battery monitoring on ADC pin 35
        battery_adc = ADC(Pin(35))
        battery_adc.atten(ADC.ATTN_11DB)
        raw_value = battery_adc.read()
        voltage = raw_value / 4095 * 3.3 * 4  # Voltage divider
        return voltage
        
    def send_data_to_server(self, data):
        """Send sensor data to server"""
        try:
            headers = {'Content-Type': 'application/json'}
            response = urequests.post(API_ENDPOINT, 
                                    data=json.dumps(data), 
                                    headers=headers)
            print("Data sent successfully:", response.status_code)
            return True
        except Exception as e:
            print("Error sending data:", e)
            return False
            
    def run_monitoring_cycle(self):
        """Main monitoring cycle"""
        if not self.connect_wifi():
            print("Failed to connect to WiFi")
            return
            
        while True:
            try:
                # Collect sensor data
                sensor_data = self.collect_sensor_data()
                print("Sensor data:", sensor_data)
                
                # Send to server
                self.send_data_to_server(sensor_data)
                
                # Deep sleep for power saving (5 minutes)
                machine.deepsleep(300000)
                
            except Exception as e:
                print("Error in monitoring cycle:", e)
                time.sleep(60)  # Wait 1 minute before retry

# Main execution
if __name__ == "__main__":
    monitor = TeaMonitor()
    monitor.run_monitoring_cycle()
