# LibCap - Library Capacity Measurement System

## Usage
For testing Mosquitto broker locally use this docker container:
```bash
 docker run -ti -p 1883:1883 -p 9001:9001 toke/mosquitto
```
after that adapt the IP Address in the code to your own.

**For setting it up permanently** install Mosquitto per apt-install on your Raspberry Pi and create a ```.conf``` file`.
(see internet for that)
```bash
touch custom_mosquitto.conf
```
write the following inside the file
```bash
listener 1883
allow_anonymous true
```

Start the Mosquitto service again with your own config-file.
```bash
Mosquitto -c custom_mosquitto.conf
```

## Idea

## Tools

## Team

# Implementation
