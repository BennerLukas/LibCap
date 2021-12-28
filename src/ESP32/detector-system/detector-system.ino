//#include <ctime>
#include <iostream>
#include <EspMQTTClient.h>

#define SENSOR_PIN 12
#define RED_LED 14
#define GREEN_LED 13


EspMQTTClient client(
  "Alpha-II-239",
  "51361007935680578489",
  "192.168.170.68",  // MQTT Broker server ip
  "",   // Can be omitted if not needed
  "",   // Can be omitted if not needed
  "esp32-01",     // Client name that uniquely identify your device
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
  client.subscribe("/lib-cap/occupied/1", [](const String & payload) {
    Serial.println(payload);
    if (payload=="true"){
      occupied = true;
    }
    else{
      occupied = false;
    }
    Serial.println(occupied);
  });
}


void loop() {
  delay(1000);
  client.loop();
  delay(1000);
  Serial.print(".");
  // get occupied status
  
  // set LED according to occupied status
  if (occupied == true){
      digitalWrite(RED_LED, HIGH);
      digitalWrite(GREEN_LED, LOW);
  }
  else{
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
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
    client.publish("/lib-cap/state/1", "Status Change: Low -> High - Motion");
  }
  
  // status change to "not occupied"
  else if (state == LOW && previous_state == HIGH) {
    Serial.println("Status Change: High -> Low - No Motion");
    client.publish("/lib-cap/state/1", "Status Change: High -> Low - No Motion");
  }

  // set current state to previous
  previous_state = state;  
}
