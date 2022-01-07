import paho.mqtt.client as mqtt
import time

broker_ip = "192.168.4.254"
connected = False
message_received = False
message = ""
client = None


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # print("Connected")
        global connected
        connected = True
        print("Connected")
        print("..........")
    else:
        print("Unable To Connect")


def on_message(client, userdata, message):

    # HERE Custom Code

    message = str(message.payload.decode("utf-8"))
    print("message received ", message)
    # print("message topic=", message.topic)
    message_received = True


def connection(client_name):
    global client
    client = mqtt.Client(client_name)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_ip, port=1883)


connection("PythonTest")

client.loop_start()

client.subscribe("/lib-cap/state/1")
while connected is not True or message_received is not True:
    time.sleep(2)
    client.publish("/lib-cap/occupied/1", "true")
    time.sleep(2)
    client.publish("/lib-cap/occupied/1", "false")
client.loop_forever()


# for changing occupied status
# client.publish("/lib-cap/occupied/1", "true")
# client.publish("/lib-cap/occupied/1", "false")
