<div align="center">
<h2>LibCap - Library Capacity Measurement System</h2>

<img src="Docs/LibCap_simple_black.png.png" alt="Logo" width="210" align="center"/>
<br>
</div>

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
The idea is a system that detects the occupancy of workstations passively, so without user interventions.

With this system, users can find free places easily and can check whether a trip to library is even needed.

## Tools
In this project where used quite a lot of new (at least for us) and cutting edge technologies. Reaching from database over container to messaging brokers.



<img src="https://img.shields.io/badge/Postgres-grey?style=flat-square&logo=postgresql"/>
<img src="https://img.shields.io/badge/Docker-grey?style=flat-square&logo=docker"/>
<img src="https://img.shields.io/badge/Flask-grey?style=flat-square&logo=flask"/>
<img src="https://img.shields.io/badge/Bootstrap-grey?style=flat-square&logo=bootstrap"/>
<img src="https://img.shields.io/badge/HTML-grey?style=flat-square&logo=html5"/>
<img src="https://img.shields.io/badge/CSS-grey?style=flat-square&logo=css3"/>
<img src="https://img.shields.io/badge/JavaScript-grey?style=flat-square&logo=JavaScript"/>
<img src="https://img.shields.io/badge/Arduino-grey?style=flat-square&logo=arduino"/>
<img src="https://img.shields.io/badge/ESP32-grey?style=flat-square&logo=espHome"/>
<img src="https://img.shields.io/badge/C++-grey?style=flat-square&logo=c"/>
<img src="https://img.shields.io/badge/Mosquitto-grey?style=flat-square&logo=Eclipse Mosquitto"/>



## Team

The team consists of 4 People. The planing and brainstorming was done in team-meetings with the help of Github's KANBAN Boards.
We collaborated on all fields and worked together to achieve our goal. Nevertheless we decided on splitting the responsibilities in 4 areas as follows:

- Alina Buss (Research & Controlling)
- Ayman Madhour (Middleware & Timeseries)
- Philip Lange (Frontend & Container)
- Lukas Benenr (Hardware & Design)

# Implementation

LibCap is fully functional Systems on a docker-stack. It can be easily deployed on minimal hardware requirements. 
The system is designed in such way, that the frontend, middleware and hardware can work independently of each other. 
This is possible due to the use of a MQTT-Broker between the Middleware and the hardware, 
as well as on strictly not making a direct connection between the frontend and middleware. All communication is over the database.

Therefore, the system is easily scalable and the components can be switched or enhanced without much hustle.


For a quick demonstration see here: https://youtu.be/ml8fKBpgCN8

<iframe width="560" height="315" src="https://www.youtube.com/embed/ml8fKBpgCN8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>