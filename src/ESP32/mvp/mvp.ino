//#include <ctime>
// #include <iostream>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>

#define SENSOR_PIN 12
#define RED_LED 14
#define GREEN_LED 13

// using namespace std;


// Replace the next variables with your SSID/Password combination
const char* ssid = "Alpha-II-239";//"Kaer Morhen";
const char* password = "51361007935680578489";

// Add your MQTT Broker IP address, example:
const char* mqtt_server = "maqiatto.com";

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;
int id = 1; // ID of the microcontroller -> given by the parent system
bool previous_state = LOW;
bool occupied = false;
boolean state = false;

void setup() {
  Serial.println("Init Programm");

  Serial.begin(9600); // init serial communication at 9600 bits/s
  pinMode(SENSOR_PIN, INPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  led_activate(RED_LED);
  led_activate(GREEN_LED);
  delay(1000);
  led_deactivate(RED_LED);
  led_deactivate(GREEN_LED);
  
  Serial.println("Init Finished");

}

void loop() {
  delay(100);

  // get occupied status
  
  // set LED according to occupied status
  if (occupied == true){
      led_activate(RED_LED);
      led_deactivate(RED_LED);
  }
  else{
    led_activate(GREEN_LED);
    led_deactivate(GREEN_LED);
  }

  // get sensor state
  state = digitalRead(SENSOR_PIN);

  // continue if no status change
  if (state == previous_state) {
    loop(); // equal to continue;
  }

  // potential status change to "occupied"
  if (state == HIGH && previous_state == LOW) {
    Serial.println("Status Change: Low -> High - Motion");
  }
  
  // status change to "not occupied"
  else if (state == LOW && previous_state == HIGH) {
    Serial.println("Status Change: High -> Low - No Motion");
  }

  // set current state to previous
  previous_state = state;



}
