import paho.mqtt.client as mqtt
import time


connected = False


class VirtualSensor:

    def __init__(self):
        self.client = self.init_connect(sensor_id=2)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            connected = True
            print("Connected")
        else:
            print("Not Able To Connect")

    def on_message(self, client, userdata, message):
        topic = message.topic
        message = str(message.payload.decode("utf-8"))
        print(f"[Topic: {topic}] Message: {message}")
        message_received = True

    def init_connect(self, sensor_id, broker_address="localhost"):

        client = mqtt.Client(f"P{sensor_id}")
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(broker_address)
        time.sleep(0.4)
        client.loop_start()
        testnum = 0
        client.subscribe(f"/lib-cap/occupied/{sensor_id}")
        return client

    def execute(self):
        while True:
            client.publish("/lib-cap/state/1", 1)
            print("Publishing... ", 1)
            testnum += 1
            time.sleep(3)

        client.loop_stop()


if __name__ == "__main__":
    pass