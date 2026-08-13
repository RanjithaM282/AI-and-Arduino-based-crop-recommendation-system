/*
  Arduino Sensor Code for Smart Agriculture System
  Sends temperature, humidity, and soil moisture data to backend
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://YOUR_BACKEND_IP:5000/arduino/sensor-data";

// DHT22 Sensor Configuration
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// Soil Moisture Sensor Configuration
#define SOIL_MOISTURE_PIN A0

// Variables to store sensor readings
float temperature = 0.0;
float humidity = 0.0;
int soilMoisture = 0;

// Timing variables
unsigned long previousMillis = 0;
const long interval = 5000; // Send data every 5 seconds

void setup() {
  Serial.begin(115200);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Initialize soil moisture sensor
  pinMode(SOIL_MOISTURE_PIN, INPUT);
  
  // Connect to WiFi
  connectWiFi();
  
  Serial.println("🌱 Arduino Smart Agriculture System Started");
  Serial.println("📡 Sending sensor data every 5 seconds");
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
  // Read temperature and humidity from DHT22
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();
  
  // Check if readings are valid
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("❌ Failed to read from DHT sensor!");
    return;
  }
  
  // Read soil moisture (0-1023, convert to 0-100%)
  soilMoisture = analogRead(SOIL_MOISTURE_PIN);
  soilMoisture = map(soilMoisture, 1023, 0, 0, 100);
  
  // Constrain values
  soilMoisture = constrain(soilMoisture, 0, 100);
  
  // Print sensor readings
  Serial.println("🌡️ Sensor Readings:");
  Serial.print("🌡️ Temperature: ");
  Serial.print(temperature);
  Serial.println("°C");
  Serial.print("💧 Humidity: ");
  Serial.print(humidity);
  Serial.println("%");
  Serial.print("🌱 Soil Moisture: ");
  Serial.print(soilMoisture);
  Serial.println("%");
  Serial.println("------------------------");
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
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["soil_moisture"] = soilMoisture;
  
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

// Function to test sensors manually
void testSensors() {
  Serial.println("🧪 Testing all sensors...");
  
  readSensors();
  
  // Test each sensor individually
  Serial.println("🌡️ Testing DHT22 sensor...");
  float testTemp = dht.readTemperature();
  float testHum = dht.readHumidity();
  
  if (isnan(testTemp) || isnan(testHum)) {
    Serial.println("❌ DHT22 sensor failed!");
  } else {
    Serial.println("✅ DHT22 sensor working!");
  }
  
  Serial.println("🌱 Testing soil moisture sensor...");
  int testMoisture = analogRead(SOIL_MOISTURE_PIN);
  Serial.print("🌱 Raw soil moisture value: ");
  Serial.println(testMoisture);
  
  if (testMoisture >= 0 && testMoisture <= 1023) {
    Serial.println("✅ Soil moisture sensor working!");
  } else {
    Serial.println("❌ Soil moisture sensor failed!");
  }
  
  Serial.println("🧪 Sensor test complete!");
}
