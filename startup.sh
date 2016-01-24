#!/usr/bin/env bash

# start the web server
cd ~/mirror
~/.envs/mirror/bin/python3 mirrorapp.py &
until $(curl --output /dev/null --silent --head --fail http://localhost:5000/alive); do
    printf '.'
    sleep 5
done

# start the browser
epiphany-browser http://localhost:5000/ &
sleep 15
xte "key F11" -x:0
