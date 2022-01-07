//#include <ctime>
#include <iostream>
#include <EspMQTTClient.h>

#define SENSOR_PIN 12
#define RED_LED 14
#define GREEN_LED 13

const char* sub_topic = "/lib-cap/occupied/1";
const char* pub_topic = "/lib-cap/state/1";
const char* controler_name = "esp32-01";
const char* broker_ip = "192.168.4.254";
const char* wifi_name = "Kaer Morhen";
const char* wifi_pwd = "3Hexerhexen";


EspMQTTClient client(
  wifi_name,
  wifi_pwd,
  broker_ip,  // MQTT Broker server ip
  "",   // Can be omitted if not needed
  "",   // Can be omitted if not needed
  controler_name,       // Client name that uniquely identify your device
  1883              // The MQTT port, default to 1883. this line can be omitted
);

bool previous_state = LOW;
bool occupied = false;
boolean state = false;

void setup() {
  Serial.println("Init Programm");

  Serial.begin(9600); // init serial communication at 9600 bits/s
  pinMode(SENSOR_PIN, INPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  client.enableDebuggingMessages();

  digitalWrite(RED_LED, HIGH);
  digitalWrite(GREEN_LED, HIGH);
  delay(1000);
  digitalWrite(RED_LED, LOW);
  digitalWrite(GREEN_LED, LOW);

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
  // delay(100);
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
  state = digitalRead(SENSOR_PIN);

  // continue if no status change
  if (state != previous_state) {
    // potential status change to "occupied"
    if (state == HIGH && previous_state == LOW) {
      Serial.println("\nStatus Change: Low -> High - Motion");
      client.publish(pub_topic, "Status Change: Low -> High - Motion");
    }
    // status change to "not occupied"
    else if (state == LOW && previous_state == HIGH) {
      Serial.println("\nStatus Change: High -> Low - No Motion");
      client.publish(pub_topic, "Status Change: High -> Low - No Motion");
    }
  }

  // set current state to previous
  previous_state = state;
}
