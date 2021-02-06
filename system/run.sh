#!/usr/bin/env bash

# Use this script to start the mirror server the first time
# or to update to a newer version.

set -euo pipefail

echo "> Removing previous container"
docker stop mirror || true && docker rm mirror || true

echo "> Running latest image as a new container"
docker run \
    -d \
    --name="mirror" \
    -p 5000:5000 \
    --pull=always \
    --restart=always \
    --volume="/home/pi/mirror/instance:/home/appuser/instance" \
    -e TZ=America/Denver \
    "genericmoniker/mirror:main"
