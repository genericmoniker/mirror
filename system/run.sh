#!/usr/bin/env bash

# Start the mirror server the first time or update to a newer version.

set -euo pipefail

echo "> Pulling latest image"
docker pull "genericmoniker/mirror:main"

echo "> Removing previous container"
docker stop mirror || true && docker rm mirror || true

echo "> Running latest image as a new container"
docker run \
    -d \
    --name="mirror" \
    -p 5000:5000 \
    --restart=always \
    --volume="/home/pi/mirror/instance:/home/appuser/instance" \
    -e TZ=America/Denver \
    "genericmoniker/mirror:main"

echo "> Removing dangling images"
docker image rm $(docker images -qa -f 'dangling=true') || true
