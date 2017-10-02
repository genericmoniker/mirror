#!/usr/bin/env bash

# start the web server
cd ~/mirror
~/.envs/mirror/bin/python3 mirrorapp.py &
until $(curl --output /dev/null --silent --head --fail http://localhost:5000/alive); do
    printf '.'
    sleep 5
done

# start the browser
/var/lib/chromium-browser/chromium-browser --incognitops --noerrdialogs --disable-session-crashed-bubble --disable-infobars --kiosk http://localhost:5000 &
