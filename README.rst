Chicken Door Control using Python, MQTT and JS-WebApp:

1. A Raspberry Pi is running the Python door control software and triggers two relays for open/close commands.
   It may have a unreliable Wifi connection to the MQTT broker and still operates automatically.
2. A MQTT broker (= server) is used to store the current and last data. It also passes manual force operations from the web app to the Raspberry.
3. A JavaScript wep application lets you control the door and check everything which is important.

Operation modes:

- sunrise and sunset based open/close times according to your position
- static open/close time
- force mode until a timeout occurs
