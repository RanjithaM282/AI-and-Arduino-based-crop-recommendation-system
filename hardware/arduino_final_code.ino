/*
  Arduino Sensor Code for Smart Agriculture System
  Uses DHT11 sensor and Soil Moisture sensor
  Sends temperature, humidity, and soil moisture data to backend
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// WiFi Configuration - UPDATE THESE VALUES
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://localhost:5000/arduino/sensor-data"; // Change to your backend IP

// DHT11 Sensor Configuration
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// Soil Moisture Sensor Configuration
#define SOIL_PIN A0

// Variables to store sensor readings
float temp = 0.0;
float hum = 0.0;
int soilValue = 0;
int moisturePercent = 0;

// Timing variables
unsigned long previousMillis = 0;
const long interval = 5000; // Send data every 5 seconds

void setup() {
  Serial.begin(9600);
  
  // Initialize DHT11 sensor
  dht.begin();
  
  // Initialize soil moisture sensor
  pinMode(SOIL_PIN, INPUT);
  
  // Connect to WiFi
  connectWiFi();
  
  Serial.println("🌱 Arduino Smart Agriculture System Started");
  Serial.println("📡 DHT11 + Soil Moisture Sensors Active");
  Serial.println("🔄 Sending data every 5 seconds");
}

void loop() {
  unsigned long currentMillis = millis();
  
  // Send data at specified interval
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    
    // Read sensor data
    readSensors();
    
    // Send data to backend
    sendSensorData();
  }
  
  delay(100);
}

void connectWiFi() {
  Serial.print("🔗 Connecting to WiFi...");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("📍 IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ Failed to connect to WiFi");
    Serial.println("🔄 Retrying in 10 seconds...");
    delay(10000);
    connectWiFi(); // Retry connection
  }
}

void readSensors() {
  // Read temperature and humidity from DHT11
  hum = dht.readHumidity();
  temp = dht.readTemperature();
  
  // Check if readings are valid
  if (isnan(hum) || isnan(temp)) {
    Serial.println("❌ Failed to read from DHT sensor!");
    return;
  }
  
  // Read soil moisture (0-1023, convert to 0-100%)
  soilValue = analogRead(SOIL_PIN);
  moisturePercent = map(soilValue, 1023, 0, 0, 100);
  
  // Constrain values
  moisturePercent = constrain(moisturePercent, 0, 100);
  
  // Print sensor readings
  Serial.println("---- Sensor Data ----");
  Serial.print("🌡️ Temperature: ");
  Serial.print(temp);
  Serial.println(" °C");
  
  Serial.print("💧 Humidity: ");
  Serial.print(hum);
  Serial.println(" %");
  
  Serial.print("🌱 Soil Moisture: ");
  Serial.print(moisturePercent);
  Serial.println(" %");
  
  Serial.println("--------------------");
}

void sendSensorData() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("❌ WiFi not connected. Reconnecting...");
    connectWiFi();
    return;
  }
  
  HTTPClient http;
  
  // Create JSON document
  DynamicJsonDocument doc(256);
  doc["temperature"] = temp;
  doc["humidity"] = hum;
  doc["soil_moisture"] = moisturePercent;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Send HTTP POST request
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  
  Serial.print("📡 Sending data to backend...");
  int httpResponseCode = http.POST(jsonString);
  
  if (httpResponseCode > 0) {
    Serial.print("✅ Response code: ");
    Serial.println(httpResponseCode);
    
    String response = http.getString();
    Serial.print("📥 Server response: ");
    Serial.println(response);
  } else {
    Serial.print("❌ Error on sending POST: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}

// Function to test sensors manually (call this from setup if needed)
void testSensors() {
  Serial.println("🧪 Testing all sensors...");
  
  readSensors();
  
  // Test each sensor individually
  Serial.println("🌡️ Testing DHT11 sensor...");
  float testTemp = dht.readTemperature();
  float testHum = dht.readHumidity();
  
  if (isnan(testTemp) || isnan(testHum)) {
    Serial.println("❌ DHT11 sensor failed!");
  } else {
    Serial.println("✅ DHT11 sensor working!");
  }
  
  Serial.println("🌱 Testing soil moisture sensor...");
  int testMoisture = analogRead(SOIL_PIN);
  Serial.print("🌱 Raw soil moisture value: ");
  Serial.println(testMoisture);
  
  if (testMoisture >= 0 && testMoisture <= 1023) {
    Serial.println("✅ Soil moisture sensor working!");
  } else {
    Serial.println("❌ Soil moisture sensor failed!");
  }
  
  Serial.println("🧪 Sensor test complete!");
}
