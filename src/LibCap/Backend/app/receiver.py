import paho.mqtt.client as mqtt
import time
import datetime
from app import engine, session  # DB is initiated in __init__.py

message = ""
connected = False
message_received = False
broker_address = "mosquitto"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global connected
        connected = True
        print("Connected")
        print("..........")
    else:
        print("Unable To Connect")


def on_message(client, userdata, message):
    """
        Catches incoming messages of published Topics
        and passes them on to interpret_payload()
    """
    topic = message.topic
    message = str(message.payload.decode("utf-8"))
    print(f"[Topic: {topic}] Message: {message}")
    interpret_payload(message, topic)
    message_received = True


def connection(client_name):
    """
        Establishes connection to mqtt broker and 
        assigns functions for new messages/connec-
        tion.
    """    
    global client
    client = mqtt.Client(client_name)

    client.on_message = on_message
    client.on_connect = on_connect

    print("connecting to broker")
    client.connect(broker_address, port=1883)


def interpret_payload(message, topic):
    """
        Interprets payload. Sensor sends motion 
        data. 1 is "motion detected" and 2 is 
        "no motion detected".
        
        A new motion kicks off status_occupied()
        and no motion activates the grace period.
    """
    entity_id = topic.split("/")[-1]  # e.g.: 1
    if int(message) == 1:
        status_occupied(entity_id)

    if int(message) == 0:
        # no motion detected
        # on low signal -> turn on deadmanswitch (5 min timestamp?)
        status = engine.execute('SELECT n_status_id FROM OBJECTS WHERE n_object_id= %s ;' % (entity_id)).fetchall()
        print("Current status: ", status[0][0])
        if status[0][0] == 1 or status[0][0] == 3:
            print("Entity already free")
        else:
            status_grace_period(entity_id)


def status_occupied(entity_id):
    """
        Sets the status of the sending entity to 2
        (occupied).
        Confirms changes to the sensor via publishing
        1 to /lib-cap/occupied/id.
    """
    # print current status of object
    entity = engine.execute('SELECT * FROM OBJECTS WHERE n_object_id= %s ;' % (entity_id)).fetchall()
    print("Current state:", entity)
    if len(entity) == 0:
        print("Entity doesn't exist in DB")

    elif int(entity[0][-2]) == 2:
        print("Status already up-to-date")
        # status_grace_period(entity_id) #toggle
    else:
        # send id to database and mark seat as occupied
        update = engine.execute("UPDATE OBJECTS SET n_status_id = 2 WHERE n_object_id = %s;" % (entity_id))

        # print("publishing status")
        client.publish(f"/lib-cap/occupied/{entity_id}", 1)  # publishes status=occupied to controller
        entity = engine.execute('SELECT * FROM OBJECTS WHERE n_object_id= %s ;' % (entity_id)).fetchall()
        print("New state:", entity)


def status_grace_period(entity_id):
    """
        Starts the grace period. The entity/seat
        will remain occupied (status 3) for the
        duration of the grace period.
    """
    # change status of entity
    entity = engine.execute('SELECT * FROM OBJECTS WHERE n_object_id= %s ;' % (entity_id)).fetchall()
    print("Current state:", entity)
    if len(entity) == 0:
        print("Entity doesn't exist in DB")

    elif int(entity[0][-2]) == 3:
        print("Status already up-to-date")

    else:
        # send id to database and mark seat as occupied
        update = engine.execute("UPDATE OBJECTS SET n_status_id = 3 WHERE n_object_id = %s;" % (entity_id))

        # Print
        entity = engine.execute('SELECT * FROM OBJECTS WHERE n_object_id= %s ;' % (entity_id)).fetchall()
        print("New state:", entity)


def check_status():
    """
        Periodically checks the if grace 
        period is over. If it's over then
        the entity/seat will be set free.
    """
    print("Checking")
    
    # query db for timestamp of entity
    grace_period_entities = engine.execute(
        'SELECT * FROM OBJECTS WHERE n_status_id = 3 OR n_status_id = 5 ORDER BY ts_last_change;').fetchall()
    current_time = datetime.datetime.utcnow()
    for entity in grace_period_entities:
        entity_id = entity[0]
        entity_timestamp = entity[-1]
        time_delta = current_time - entity_timestamp 
        time_delta = time_delta.seconds
        print(f"Current:{current_time}")
        print(f"Current:{entity_timestamp}")
        print(f"{entity_id}: delta = {time_delta}")

        # check timestamp difference --> if greater than n min --> purge
        if time_delta > 15:  # 5 * 60 sec
            status_free(entity_id)
            history = engine.execute('SELECT * FROM STATUS_HISTORY;').fetchall()
            print(f"history: {history}")


def status_free(entity_id):
    """
        Changes the status of the entity to 1
        (free).
        Confirms to the esp32 that the seat is
        now free via publish to lib-cap/occupied/id.
    """    
    # print current status of object
    entity = engine.execute('SELECT * FROM OBJECTS WHERE n_object_id= %s ;' % (entity_id)).fetchall()
    print("Current state:", entity)
    if len(entity) == 0:
        print("Entity doesn't exist in DB")

    elif int(entity[0][-2]) == 1:
        print("Status already up-to-date")

    else:
        print("Grace period over, changing status...")
        # send id to database and mark seat as occupied
        update = engine.execute("UPDATE OBJECTS SET n_status_id = 1 WHERE n_object_id = %s;" % (entity_id))

        entity = engine.execute('SELECT * FROM OBJECTS WHERE n_object_id= %s ;' % (entity_id)).fetchall()
        print("New state:", entity)
        # print("publishing status")
        client.publish(f"/lib-cap/occupied/{entity_id}", 0) #publishes status=free to controller


def send_reserved_payload():
    """
        Periodically checks if any entity/seat
        has been booked. 
        Confirms to esp32 that seat is reserved
        via publish to /lib-cap/occupied/id.
    """
    reserved_entities = engine.execute(
        'SELECT * FROM OBJECTS WHERE n_status_id = 5 ORDER BY ts_last_change;').fetchall()
    for entity in reserved_entities:
        entity_id = entity[0]
        client.publish(f"/lib-cap/occupied/{entity_id}", 2) #publishes status=reserved to controller
        


connection("LibCap-Backend")

client.loop_start()

print("Subscribing to topic")

client.subscribe("/lib-cap/state/#")

# wait for message or connection
while connected != True or message_received != True:
    time.sleep(4)
    check_status()
    send_reserved_payload()

client.loop_forever()

