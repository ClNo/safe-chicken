Raspberry Base Setup
====================

OS Installation
---------------

Download the light version of the Raspberry OS from
`Raspberry Pi <https://www.raspberrypi.org/software>`_: Raspberry Pi OS Lite (size around 440 MB)

Write it on the SD card using some Flash Card Writer Tool (for instance `USB Image Tool <https://www.alexpage.de/>`_ on Windows, or just "dd" on Linux).

Then boot it and do the base settings directly via keyboard and HDMI screen as SSH is not active yet.

Base Setup
----------

:code:`sudo raspi-config`

- Localisation Options (Timezone is important)
- Interface Options: enable SSH
- change the default password for user *pi*


Disable Bluetooth
-----------------

:code:`sudo systemctl disable bluetooth`

Copy your SSH public keys
-------------------------

In order to avoid to always enter the Raspberry's user password you could copy the public key. So
from your Linux workstation desktop do this:

.. code::

   ssh-copy-id pi@<IP of Raspi>

So now it should not be necessary to always enter your password on Raspi login or scp copy operations.


Misc
----

For convinience, the widely used shell aliases could be enabled:

.. code::

   nano /home/pi/.bashrc

Uncomment the already existing lines so they look like this:

.. code::

   # some more ls aliases
   alias ll='ls -l'
   alias la='ls -A'
   alias l='ls -CF'

To give out the processor temperature it is recommended to make an alias called :code:`temp`:

.. code::

   nano /home/pi/.bash_aliases

.. code::

   alias temp='/opt/vc/bin/vcgencmd measure_temp'

After a re-login you can get the temperature by calling *temp*:

.. code::

   pi@raspberrypi:~ $ temp
   temp=40.8'C

