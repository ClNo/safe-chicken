.. Flask Squirrel documentation master file, created by
   sphinx-quickstart on Tue Jul 28 00:06:22 2020.


Welcome to Safe Chicken's documentation!
==========================================

So what is *Safe Chicken*?

- a Raspberry Pi controlling a chicken door electronics so they are safe at night
- the door can be opened or closed according to:

  - sunrise & sunset (calculated) 
  - static time
  - force command (web app open/close buttons)

- the web application helps checking the current state of the door and allowing some user commands
- the output is just a relay signal to open and close the door
- the door motor and the motor electronics are not part of this project; this setup just
  controls the relay signals (and two LEDs for displaying the status)
- uses an MQTT broker which runs on your NAS or a home server (but could also run on the Raspberry itself)
- allows unstable WLAN connections from the Raspberry to the home network

Get *Safe Chicken* on `GitHub <https://github.com/ClNo/safe-chicken>`_.

Table of Contents
=================
    
.. toctree::
   :maxdepth: 2

   overview/overview
   hardware/control_components
   docker/DockerSetup

   raspberry/base_setup
   raspberry/application_setup
   raspberry/functions
   raspberry/network_setup
   raspberry/backup_restore
   
   webapp/webapp


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
