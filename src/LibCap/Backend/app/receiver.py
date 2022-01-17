
import paho.mqtt.client as mqtt
import time
import datetime
from app import engine, session #DB is initiated in __init__.py

message = ""
connected = False
message_received = False
broker_address = "localhost"

def on_message(client, userdata, message):
    topic = message.topic
    message = str(message.payload.decode("utf-8"))
    print(f"[Topic: {topic}] Message: {message}")
    interpret_payload(message, topic)
    message_received = True

    
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        global connected
        connected = True
        print("Connected")
        print("..........")
    else:
        print("Unable To Connect")


def connection(client_name):    
    global client
    client = mqtt.Client(client_name)

    client.on_message = on_message
    client.on_connect = on_connect

    print("connecting to broker")
    client.connect(broker_address, port=1883)


def interpret_payload(message,topic):
    entity_id = topic.split("/")[-1] # e.g.: 1
    if int(message) == 1:
        #motion detected -> trigger occupied
        # set timestamp to 10h --> Not needed anymore
        status_occupied(entity_id)
        
    
    if int(message) == 0:
        #no motion detected
        # on low signal -> turn on deadmanswitch (5 min timestamp?)
        status = engine.execute('SELECT n_status_id FROM OBJECTS WHERE n_object_id= %s ;' %(entity_id)).fetchall()
        print("Current status: ",status[0][0])
        if status[0][0] == 1 or status[0][0] == 3:
            print("Entity already free")
        else:
            status_grace_period(entity_id)

        
def status_occupied(entity_id):
    #print current status of object
    entity = engine.execute('SELECT * FROM OBJECTS WHERE n_object_id= %s ;' %(entity_id)).fetchall()
    print("Current state:",entity)
    if len(entity) == 0:
        print("Entity doesn't exist in DB")
        
    elif int(entity[0][-2]) == 2:
        print("Status already up-to-date")
        
    else:
        #send id to database and mark seat as occupied
        update = engine.execute("UPDATE OBJECTS SET n_status_id = 2 WHERE n_object_id = %s;" %(entity_id))
        
        #print("publishing status")
        client.publish(f"/lib-cap/occupied/{entity_id}", "true") # entity subscribes to topic with corresponding id


def status_grace_period(entity_id):
    # change status of entity
    entity = engine.execute('SELECT * FROM OBJECTS WHERE n_object_id= %s ;' %(entity_id)).fetchall()
    print("Current state:",entity)
    if len(entity) == 0:
        print("Entity doesn't exist in DB")
        
    elif int(entity[0][-2]) == 3:
        print("Status already up-to-date")
        
    else:
        #send id to database and mark seat as occupied
        update = engine.execute("UPDATE OBJECTS SET n_status_id = 3 WHERE n_object_id = %s;" %(entity_id))


def check_status():
    # query db for timestamp of entity
    print("Checking")
    grace_period_entities = engine.execute('SELECT * FROM OBJECTS WHERE n_status_id = 3 ORDER BY ts_last_change;').fetchall()
    current_time = datetime.datetime.utcnow()    
    for entity in grace_period_entities:
        entity_id = entity[0]
        entity_timestamp = entity[-1]
        time_delta = current_time - entity_timestamp #datetime.timedelta(seconds=14400)
        time_delta = time_delta.seconds
        print(f"Current:{current_time}")
        print(f"Current:{entity_timestamp}")
        print(f"{entity_id}: delta = {time_delta}")
        
        
        # check timestamp difference --> if greater than 5 min --> purge
        if time_delta > 15: #5 * 60 sec
            status_free(entity_id)
            history = engine.execute('SELECT * FROM STATUS_HISTORY;').fetchall()
            #print(f"history: {history}")
  

def status_free(entity_id):
    #print current status of object
    entity = engine.execute('SELECT * FROM OBJECTS WHERE n_object_id= %s ;' %(entity_id)).fetchall()
    print("Current state:",entity)
    if len(entity) == 0:
        print("Entity doesn't exist in DB")
        
    elif int(entity[0][-2]) == 1:
        print("Status already up-to-date")
        
    else:
        print("Grace period over, changing status...")
        # send id to database and mark seat as occupied
        update = engine.execute("UPDATE OBJECTS SET n_status_id = 1 WHERE n_object_id = %s;" %(entity_id))
        
        #print("publishing status")
        client.publish(f"/lib-cap/occupied/{entity_id}", "false")



connection("LibCap-Backend")

client.loop_start()

print("Subscribing to topic")
#client.subscribe("/lib-cap/+/state")
client.subscribe("/lib-cap/state/#")

#wait for message or connection
while connected != True or message_received != True:
    time.sleep(4)
    check_status()


client.loop_forever()


# code for shell
# A '#' character represents a complete sub-tree of the hierarchy and thus must be the last character in a subscription topic string, such as SENSOR/#. This will match any topic starting with SENSOR/, such as SENSOR/1/TEMP and SENSOR/2/HUMIDITY.
# A '+' character represents a single level of the hierarchy and is used between delimiters. For example, SENSOR/+/TEMP will match SENSOR/1/TEMP and SENSOR/2/TEMP.
