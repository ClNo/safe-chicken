Raspberry Network Setup
=======================

Ethernet
--------

:code:`sudo nano /etc/dhcp/dhclient.conf`

*For static IP, consult /etc/dhcpcd.conf and 'man dhcpcd.conf'*



WLAN
----

See :ref:`https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md`

:code:`sudo raspi-config`

- Change WLAN country option

If you have two networks in range, you can add the priority option to choose between them. The network in range, with the highest priority, will be the one that is connected.

:code:`sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`

.. code::

   network={
       ssid="HomeOneSSID"
       psk="passwordOne"
       priority=1
       id_str="homeOne"
   }

   network={
       ssid="HomeTwoSSID"
       psk="passwordTwo"
       priority=2
       id_str="homeTwo"
   }
