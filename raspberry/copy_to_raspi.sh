#!/bin/bash

RASPIIP="${1}"
RASPISSH="pi@${RASPIIP}"
REMOTE_BASEDIR="/home/pi/safe-chicken"

ssh "${RASPISSH}" "mkdir -p ${REMOTE_BASEDIR}"

# --- 1. copy everything except the venv

scp -r docroot raspberry safechicken tests config.json requirements.txt "${RASPISSH}:${REMOTE_BASEDIR}/"

if [[ $? -ne 0 ]]; then
  echo "copy failed"
  exit 1
fi

# --- 2. create the venv if it's not done yet

ssh "${RASPISSH}" "cd ${REMOTE_BASEDIR}; if [[ ! -e venv ]]; then sudo apt install -y python3-venv; python3 -m venv venv; source venv/bin/activate; pip install --upgrade pip; pip install -r requirements.txt; fi"

# --- 3. install the system start service if it's not done yet

ssh "${RASPISSH}" "cd ${REMOTE_BASEDIR}; if [[ ! -e /etc/systemd/system/safechicken.service ]]; then sudo cp raspberry/safechicken.service /etc/systemd/system/; sudo systemctl daemon-reload; sudo systemctl enable safechicken.service; fi"
