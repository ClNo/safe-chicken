Door Control Components
=======================

.. table:: Hardware Components

   == =================================== ===================================
   No Part Name                           Usage
   == =================================== ===================================
   1  Raspberry 3 or 4 with power supply  door controller
   2  M5Stack Mini 3A Relay Unit U023     door open relay
   3  M5Stack Mini 3A Relay Unit U023     door close relay
   4  M5Stack Hall Sensor U084            magnetic sensor for door closed
   5  M5Stack 1 to 3 HUB Unit U006        sensor cable extension
   6  M5Stack Unbuckled Grove Cable 50cm  sensor cable extension
      A034-C
   7  Adafruit Jumperset 40 wires         Raspi GPIO connection
      male/female, 15cm
   8  orange LED 11 mA + resistor 82 Ohms automatic is working (= time synced)
   9  green LED 11 mA + resistor 82 Ohms  MQTT connection to broker working
   == =================================== ===================================


Raspberry GPIO connection:

.. image:: /_static/hardware/gpio_connection.svg
   :scale: 150 %

This I/O configuration can be found on the Python/Raspberry side as *config.json*:

.. code-block:: json

    {
        "io": {
            "out_ready_led": 4,
            "out_network_status_led": 17,
            "out_open_command": 5,
            "out_close_command": 6,
            "in_door_closed": {"pin": 25, "active_state": true},
            "command_out_pulse_time_s": 2
        }
    }

The Raspberry is enclosed in a case which is waterproof so there will not be any condensed water. It's good enougth to control the relays.

.. image:: Raspberry_in_case.JPG
