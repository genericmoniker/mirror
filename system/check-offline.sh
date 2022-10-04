#!/usr/bin/env bash

set -e

# Check for the offline file and reboot the system if it exists.
while true; do
    sleep 60
    if [ -f /home/pi/mirror/instance/mirror-offline ]; then
        rm /home/pi/mirror/instance/mirror-offline
        echo "$(date +"%m/%d/%Y %H:%M:%S) Offline file detected. Rebooting." >> /home/pi/mirror/instance/mirror-offline.log
        reboot
    fi
done
