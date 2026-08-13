/*
  Simple Arduino Test for Troubleshooting
  Send basic JSON data every 2 seconds
*/

void setup() {
  Serial.begin(9600);
  Serial.println("Arduino Test Started");
}

void loop() {
  // Send JSON test data
  Serial.print("{\"temp\":25.5,\"hum\":65.0,\"soil\":45.2}");
  Serial.println();
  
  delay(2000);
}
