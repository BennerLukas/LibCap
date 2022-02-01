# Code for Debug

import paho.mqtt.client as mqtt
import time

connected = False


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        connected = True
        print("Connected")
    else:
        print("Not Able To Connect")
        
def on_message(client, userdata, message):
    topic = message.topic
    message = str(message.payload.decode("utf-8"))
    print(f"[Topic: {topic}] Message: {message}")
    message_received = True


broker_address = "localhost"

client = mqtt.Client("P1")
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address)
time.sleep(0.4)
client.loop_start()
testnum = 0
client.subscribe("/lib-cap/occupied/2")
while True:
    client.publish("/lib-cap/state/2", 1)
    print("Publishing... ", 1)
    testnum += 1
    time.sleep(3)
    client.publish("/lib-cap/state/2", 0)
    print("Publishing... ", 0)
    time.sleep(16)
    client.publish("/lib-cap/state/2", 1)
    print("Publishing... ", 1)


client.loop_stop()
