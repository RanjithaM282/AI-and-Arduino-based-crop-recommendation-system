/*
  Final Clean Arduino Code - ABSOLUTELY NO DEBUG MESSAGES
  Sends ONLY JSON data for backend communication
*/

#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define SOIL_PIN A0

float temp = 0.0;
float hum = 0.0;
int soilValue = 0;
int moisturePercent = 0;

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  hum = dht.readHumidity();
  temp = dht.readTemperature();
  
  if (!isnan(hum) && !isnan(temp)) {
    soilValue = analogRead(SOIL_PIN);
    moisturePercent = map(soilValue, 1023, 0, 0, 100);
    moisturePercent = constrain(moisturePercent, 0, 100);
    
    // Send ONLY JSON data - NO DEBUG MESSAGES
    Serial.print("{\"temp\":");
    Serial.print(temp);
    Serial.print(",\"hum\":");
    Serial.print(hum);
    Serial.print(",\"soil\":");
    Serial.print(moisturePercent);
    Serial.println("}");
  }
  
  delay(2000);
}
