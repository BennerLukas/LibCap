
int led_activate(int led){
  boolean state = digitalRead(led); 
  if (state == LOW){
    digitalWrite(led, HIGH); // turn the LED on
    return 0;
  }
  else {
    Serial.println("LED was already activated");
    return -1;
  }
}

int led_deactivate(int led){
  boolean state = digitalRead(led); 
  if (state == HIGH){
    digitalWrite(led, LOW); // turn the LED off
    return 0;
  }
  else {
    Serial.println("LED was already deactivated");
    return -1;
  }
}