#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <string>

#define SENSOR_PIN 12
#define RED_LED 14
#define GREEN_LED 13

// Replace the next variables with your SSID/Password combination
const char* ssid = "Alpha-II-239";//"Kaer Morhen";
const char* password = "51361007935680578489"; //"3Hexerhexen";

// Add your MQTT Broker IP address, example:
//const char* mqtt_server = "192.168.1.144";
const char* mqtt_server = "192.168.170.68";

const char* pub_topic = "lib-cap/state/1";
const char* sub_topic = "lib-cap/occupied/1";


WiFiClient espClient;
PubSubClient client(espClient);

// not needed
long lastMsg = 0;
char msg[50];
int value = 0;

boolean state = false;
std::string state_msg;
 
void setup() {
  Serial.begin(9600);
  // default settings
  // (you can also pass in a Wire library object like &Wire2)
  
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  pinMode(SENSOR_PIN, INPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String msg;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    msg += (char)message[i];
  }
  Serial.println();

  // Feel free to add more if statements to control more GPIOs with MQTT

  // If a message is received on the topic esp32/output, you check if the message is either "on" or "off". 
  // Changes the output state according to the message
//  if (String(topic) == pub_topic) {
//    Serial.print("Changing output to ");
//    if(messageTemp == "on"){
//      Serial.println("on");
//      digitalWrite(ledPin, HIGH);
//    }
//    else if(messageTemp == "off"){
//      Serial.println("off");
//      digitalWrite(ledPin, LOW);
//    }
//  }
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      // Subscribe
      client.subscribe(sub_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 5000) {
    lastMsg = now;
    Serial.print("Status is: ");
    state = digitalRead(SENSOR_PIN);   
    if (state == HIGH) {
      Serial.println("Motion");
      client.publish(pub_topic, "Motion");
    }
    else{
      Serial.println("No Motion");
      client.publish(pub_topic, "No Motion");
    }
    



  }
}
