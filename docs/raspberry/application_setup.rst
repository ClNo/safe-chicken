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
