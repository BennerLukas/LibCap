#include <ctime>
#include <iostream>

#define SENSOR_PIN 12
#define LED_PIN 14

using namespace std;

int id = 1; // ID of the microcontroller -> given by the parent system
bool previous_state = LOW;
bool occupied = false;

void setup() {

  Serial.begin(9600); // init serial communication at 9600 bits/s
  pinMode(SENSOR_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);

  led_activate(LED_PIN);
}

void loop() {
  delay(100);

  // get occupied status

  // set LED according to occupied status


  // get sensor state
  boolean state = digitalRead(SENSOR_PIN);

  // continue if no status change
  if (state == previous_state) {
    loop(); // equal to continue;
  }

  // potential status change to "occupied"
  if (state == HIGH && previous_state == LOW) {

  }
  
  // status change to "not occupied"
  else if (state == LOW && previous_state == HIGH) {

  }

  // set current state to previous
  previous_state = state;



}