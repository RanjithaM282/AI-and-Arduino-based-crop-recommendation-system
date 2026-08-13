/*
  Arduino Sensor Code for Smart Agriculture System
  Sends JSON data via Serial for backend communication
  Uses DHT11 sensor and Soil Moisture sensor
*/

#include <DHT.h>

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

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  // Read sensor data
  readSensors();
  
  // Send JSON data via Serial
  sendJsonData();
  
  delay(2000); // Send every 2 seconds
}

void readSensors() {
  // Read temperature and humidity from DHT11
  hum = dht.readHumidity();
  temp = dht.readTemperature();
  
  // Check if readings are valid
  if (isnan(hum) || isnan(temp)) {
    return;
  }
  
  // Read soil moisture (0-1023, convert to 0-100%)
  soilValue = analogRead(SOIL_PIN);
  moisturePercent = map(soilValue, 1023, 0, 0, 100);
  
  // Constrain values
  moisturePercent = constrain(moisturePercent, 0, 100);
}

void sendJsonData() {
  // Send JSON format for backend parsing
  Serial.print("{\"temp\":");
  Serial.print(temp);
  Serial.print(",\"hum\":");
  Serial.print(hum);
  Serial.print(",\"soil\":");
  Serial.print(moisturePercent);
  Serial.println("}");
}

// Function to test sensors manually
void testSensors() {
  readSensors();
}
