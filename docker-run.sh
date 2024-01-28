#!/bin/bash

# This is for running docker for dev/test purposes.
# See system/run.sh for running the app in production.

set -euo pipefail

# Mounted volumes on Windows ideally come from the Linux filesystem,
# but it probably doesn't matter in our case. If this doesn't work
# try just entering the path to the "instance" directory here:
HOST_VOLUME="$(readlink -f instance)"

IMAGE_NAME="genericmoniker/mirror"

docker run \
    -d \
    --name="mirror" \
    -p 5000:5000 \
    --volume="${HOST_VOLUME}:/home/appuser/instance" \
    -e TZ=America/Denver \
    "${IMAGE_NAME}:main"
