#!/bin/bash

set -euo pipefail

# Wait for the mirror server to be ready.
until $(curl --output /dev/null --silent --head --fail http://localhost:5000/ready); do
    sleep 1
done

# Start the browser.
chromium-browser --incognito --noerrdialogs --disable-session-crashed-bubble --disable-infobars --kiosk http://localhost:5000

# Alternative browser command.
# /usr/bin/firefox -kiosk -private-window http://localhost:5000
