#!/bin/bash

#-------------------------------------------------------------------------------
# this file is started in the system start and runs as root
#-------------------------------------------------------------------------------

PROJ_BASEPATH="/home/pi/safe-chicken"

cd ${PROJ_BASEPATH}

mkdir -p log
if [ -e log/application.log ]; then
  mv log/application.log log/application_old.log
fi

chown -R pi:pi log
su pi -c 'source venv/bin/activate && /bin/bash -c "python3 -m safechicken.main config.json --logfile log/application.log &"'
