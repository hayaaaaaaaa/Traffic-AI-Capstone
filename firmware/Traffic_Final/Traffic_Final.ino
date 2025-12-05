#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

const char* ssid = "HHJM";
const char* password = "seuzcanal75";
String baseUrl = "http://192.168.1.13:5000"; //Change to ur pc ip (in cmd-> ipconfig)

// Pin Definitions
#define R1_G 14
#define R1_Y 12
#define R1_R 13
#define R2_G 25
#define R2_Y 26
#define R2_R 27
#define S1_PIN 4
#define S2_PIN 2

Servo s1; Servo s2;

void setup() {
  Serial.begin(115200);
  
  // Initialize Pins
  pinMode(R1_G,OUTPUT);
  pinMode(R1_Y,OUTPUT);
  pinMode(R1_R,OUTPUT);
  pinMode(R2_G,OUTPUT);
  pinMode(R2_Y,OUTPUT);
  pinMode(R2_R,OUTPUT);
  
  // Initialize Servos
  s1.attach(S1_PIN);
  s2.attach(S2_PIN);
  
  // Set Safe State (Gates Open, Reds On)
  s1.write(90);
  s2.write(90);
  digitalWrite(R1_R, HIGH);
  digitalWrite(R2_R, HIGH);
  
  // Wi-Fi Connection
  Serial.print("Connecting to WiFi...");
  WiFi.begin(ssid, password);
  while(WiFi.status()!=WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connected!");

  // === MASTER SYNC: RESET SERVER ON BOOT ===
  // When you press the EN button on ESP32, it restarts, runs setup(), 
  // and sends this command to Python to set time to 0s.
  Serial.println(">>> SENDING SYNC SIGNAL...");
  HTTPClient http;
  http.begin(baseUrl + "/reset_system");
  int code = http.GET();
  if (code > 0) {
    Serial.println(">>> SYNC SUCCESS. TIMELINE STARTED.");
    // Visual confirmation: Blink Green Lights
    digitalWrite(R1_G, HIGH);
    digitalWrite(R2_G, HIGH);
    delay(500);
    digitalWrite(R1_G, LOW);
    digitalWrite(R2_G, LOW);
  } else {
    Serial.println("!!! SYNC FAILED. CHECK IP ADDRESS !!!");
  }
  http.end();
  // =========================================
}

void loop() {
  if(WiFi.status()==WL_CONNECTED){
    HTTPClient http;
    http.begin(baseUrl + "/telemetry");
    
    if(http.GET() > 0){
      String payload = http.getString();
      
      // Parse JSON
      StaticJsonDocument<512> doc;
      deserializeJson(doc, payload);
      
      String light = doc["decision"];
      int v1 = doc["servo1"];
      int v2 = doc["servo2"];
      
      // Control Lights
      controlLights(light);
      
      // Control Servos
      s1.write(v1); 
      s2.write(v2);
    }
    http.end();
  }
  delay(200); // Check 5 times per second for fast response
}

void controlLights(String greenRoad) {
  // Turn off Yellows
  digitalWrite(R1_Y,LOW);
  digitalWrite(R2_Y,LOW);
  
  if(greenRoad == "ROAD1"){
    // Road 1 Green, Road 2 Red
    digitalWrite(R1_G,HIGH);
    digitalWrite(R1_R,LOW);
    digitalWrite(R2_G,LOW);
    digitalWrite(R2_R,HIGH);
  } else {
    // Road 1 Red, Road 2 Green
    digitalWrite(R1_G,LOW);
    digitalWrite(R1_R,HIGH);
    digitalWrite(R2_G,HIGH);
    digitalWrite(R2_R,LOW);
  }
}
