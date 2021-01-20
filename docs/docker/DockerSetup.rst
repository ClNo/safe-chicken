MQTT Broker Docker Setup
========================

Variant
-------

Docker eclipse-mosquitto

version 1.6, no SSL because of certificates


Host Persistend Directories
---------------------------

Make directory for :code:`/Container/eclipse-mosquitto-16`

Create following directories in it:

.. code::

   config
   data
   docroot
   log


Create an initial configuration in :code:`config/mosquitto.conf`:

.. code::

   persistence true
   persistence_location /mosquitto/data/
   log_dest file /mosquitto/log/mosquitto.log

   listener 9001
   protocol websockets
   http_dir /mosquitto/docroot


Container Configuration
-----------------------

Name: eclipse-mosquitto-2020
Command: /usr/sbin/mosquitto -c /mosquitto/config/mosquitto.conf
Entrypoint: /docker-entrypoint.sh
CPU Limit: 10%
Memory Limit: 1200 MB

Container Hostname: mqtt-16

Network, exposed ports:

- for MQTT protocol: QNAP-Host: 1883, Container: 1883, TCP
- for Websockets: QNAP-Host: 9001, Container: 9001, TCP

Shared Folders:

- Volume from host:

  - /Container/eclipse-mosquitto-16/config => /mosquitto/config
  - /Container/eclipse-mosquitto-16/data => /mosquitto/data
  - /Container/eclipse-mosquitto-16/log => /mosquitto/log


HTTP server for the Web App
---------------------------

Offical nginx

Name: nginx-safechicken
CPU Limit: 10%
Memory Limit: 1200 MB

Container Hostname: nginx-safechicken

Network, exposed ports:

- for MQTT protocol: QNAP-Host: 9000, Container: 80, TCP

- Volume from host:

  - /Container/http-safechicken/docroot => /usr/share/nginx/html

Set directory permissions:

cd /usr/share/nginx/html
chown nginx:nginx .
chown nginx:nginx -R ./*


MQTT Client
-----------

Proposed client: https://mqtt-explorer.com/

snap install mqtt-explorer

Run it like this: :code:`mqtt-explorer`


Name: <some name>
Host: <your Docker host>
Port: 1883


MQTT Manual Test
----------------

Using mqtt-explorer > Publish json

test1/topic1: {"value1":11, "array1": ["val1", "val2"]}

Select "retain" to store it in a database so you could better test it.
