#!/usr/bin/env bash

echo "Turning screen off"

# Turn dpms on (so we can use it to turn the screen off)
xset +dpms -display :0

# Turn the screen off
xset dpms force off -display :0
