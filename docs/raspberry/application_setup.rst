Application Setup
=================

Copy to Raspi
-------------

Use the helper script to copy everything needed to the Raspi:

.. code::

   cd path/to/safechicken
   raspberry/copy_to_raspi.sh <IP of your Raspberry>

This script also installs the package :code:`python3-venv` and installs the virtual environment.


Manual Start
------------

.. code::

   cd ~/safechicken
   source venv/bin/activate
   python3 -m safechicken.main config.json

Check the console logs it it's running or not and also the status LEDs.

System Auto Start
-----------------

The following code is automatically executed in the copy_to_raspi.sh script, but could be done manually on the Raspberry side:

.. code::
   
   sudo cp /home/pi/safechicken/raspberry/safechicken.service /etc/systemd/system/
   sudo chmod +x /etc/systemd/system/safechicken.service
   sudo systemctl daemon-reload
   sudo systemctl enable safechicken.service

Safe Chicken Configuration
--------------------------

Set your home coordinates in the *config.json* file otherwise the open/close times according to sunrise/sunset times does not match.
Also set the MQTT broker host name according to your home network.

.. code-block:: json

   {
     "time_control": {
       "latitude": 47.0,
       "longitude": 7.0,
       "minutes_after_sunrise": 15,
       "minutes_after_sunset": 30
     },
     "mqtt_client": {
       "broker_hostname": "192.168.21.5",
       "broker_port": 1883,
       "client_name": "SafeChickenController"
     },
     "topic_conf": {
       "sun_times": "safechicken/sun_times",
       "door_sun_times_conf": "safechicken/door_sun_times_conf",
       "door_prio": "safechicken/door_prio",
       "static_time": "safechicken/static_time",
       "force_operation": "safechicken/force_operation",
       "command_out": "safechicken/command_out",
       "last_commands": "safechicken/last_commands",
       "door_closed_log": "safechicken/door_closed_log",
       "door_lifesign": "safechicken/door_lifesign"
     },
     "controller": {
       "force_time_expire_minutes": 180
     },
     "dispatcher": {
       "start_action_delay": 2
     },
     "io": {
       "out_ready_led": 4,
       "out_network_status_led": 17,
       "out_open_command": 5,
       "out_close_command": 6,
       "in_door_closed": {"pin": 25, "active_state": true},
       "command_out_pulse_time_s": 2
     }
   }
