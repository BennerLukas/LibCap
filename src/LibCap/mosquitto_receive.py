# Code Written By Tech Notebook
# youtube.com/technotebook

import paho.mqtt.client as mqtt
import time

message = ""


def on_message(client, userdata, message):
    message = str(message.payload.decode("utf-8"))
    print("message received ", message)
    # print("message topic=", message.topic)
    message_received = True


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected")
        global connected
        connected = True
        print("Connected")
        print("..........")
    else:
        print("Unable To Connect")


connected = False
message_received = False
broker_address = "192.168.170.68"

print("creating new instance")
client = mqtt.Client("MQTT")

client.on_message = on_message
client.on_connect = on_connect

print("connecting to broker")
client.connect(broker_address, port=1883)

client.loop_start()

print("Subscribing to topic", "test")
client.subscribe("test")

while connected != True or message_received != True:
    time.sleep(0.2)

client.loop_forever()

# Code Written By Tech Notebook
# youtube.com/technotebook