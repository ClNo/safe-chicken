Functions
=========

Time Synchronisation
--------------------

SafeChicken door control only works when the system time is correct and synchronized at least once. This can manually be checked with the command:

.. code-block::

   pi@raspberrypi:~ $ timedatectl show -p NTPSynchronized
   NTPSynchronized=yes

Or in Python:

.. code-block:: python

   import subprocess 

   command = ['timedatectl', 'show', '-p', 'NTPSynchronized']
   res = subprocess.check_output(command)

   if '=yes' in res.decode("utf-8"):
       print('timesync working')
   else:
       print('timesync NOT working')

Output Signals
--------------

The door open and door close signals are both an **impulse of 2 seconds** each which let the door motor electronics
activate its motor on the requested side.
