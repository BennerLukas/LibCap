//#include <ctime>
// #include <iostream>

#define SENSOR_PIN 12
#define RED_LED 14
#define GREEN_LED 13

// using namespace std;

int id = 1; // ID of the microcontroller -> given by the parent system
bool previous_state = LOW;
bool occupied = false;
boolean state = false;

void setup() {

  Serial.begin(9600); // init serial communication at 9600 bits/s
  pinMode(SENSOR_PIN, INPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  Serial.println("Init Programm");
  led_activate(RED_LED);
  led_activate(GREEN_LED);
  delay(10000);
  led_deactivate(RED_LED);
  led_deactivate(GREEN_LED);

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

  }
  
  // status change to "not occupied"
  else if (state == LOW && previous_state == HIGH) {

  }

  // set current state to previous
  previous_state = state;



}
