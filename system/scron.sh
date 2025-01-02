#!/usr/bin/env bash

# Turn dpms on (so we can use it, just in case it is off)
xset +dpms -display :0

# Turn the screen on
xset dpms force on -display :0

# Turn dpms off so that the screen will not turn off after the timeout
xset -dpms -display :0
