//#include <ctime>
#include <iostream>
#include <EspMQTTClient.h>

#define ECHO 12
#define TRIGGER 27
#define RED_LED 14
#define GREEN_LED 13

const char* sub_topic = "/lib-cap/occupied/1";
const char* pub_topic = "/lib-cap/state/1";
const char* controler_name = "esp32-01";
const char* broker_ip = "192.168.4.254";
const char* wifi_name = "Kaer Morhen";
const char* wifi_pwd = "3Hexerhexen";
double error_correction = 0.02;

EspMQTTClient client(
  wifi_name,
  wifi_pwd,
  broker_ip,  // MQTT Broker server ip
  "",   // Can be omitted if not needed
  "",   // Can be omitted if not needed
  controler_name,       // Client name that uniquely identify your device
  1883              // The MQTT port, default to 1883. this line can be omitted
);

bool occupied = false;
int duration, distance, prev_distance;
int iter = 0;
void setup() {
  Serial.println("Init Programm");

  Serial.begin(9600); // init serial communication at 9600 bits/s
  pinMode(TRIGGER, OUTPUT);
  pinMode(ECHO, INPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  client.enableDebuggingMessages();

  digitalWrite(RED_LED, HIGH);
  digitalWrite(GREEN_LED, HIGH);
  delay(1000);
  digitalWrite(RED_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
  prev_distance =1;
  Serial.println("Init Finished");
}


void onConnectionEstablished()
{
  Serial.println("connected to mqtt\n");    //lambda payload: payload....
  client.subscribe(sub_topic, [](const String & payload) {
    Serial.println(payload);
    if (payload == "true") {
      occupied = true;
    }
    else {
      occupied = false;
    }
    Serial.println(occupied);
  });
}


void loop() {
  delay(100);
  client.loop();
  Serial.print(".");
  // get occupied status

  // set LED according to occupied status
  if (occupied == true) {
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
  }
  else {
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
  }

  // get sensor state
  digitalWrite(TRIGGER, HIGH);
  delay(500);
  digitalWrite(TRIGGER, LOW);
  duration = pulseIn(ECHO, HIGH);
  distance = (duration/2) / 29.1; 
  
  // continue if no status change
  if ((distance > prev_distance * (1 + error_correction)) || (distance < prev_distance * (1 - error_correction))) { // if outside of error correction
    // potential status change to "occupied"
    // distance change -> movement
    Serial.println("\nDistance Change: Movement");
    client.publish(pub_topic, "1");
    delay(1000);
  }

  // set current state to previous
  prev_distance = distance;
}
