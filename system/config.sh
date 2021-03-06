#!/usr/bin/env bash

# Configure the mirror interactively.
# Script arguments are passed to mirror-config:
# ./config.sh --plugins mail worth

set -euo pipefail

docker run \
    --name="mirror-config" \
    -it \
    --rm \
    --volume="/home/pi/mirror/instance:/home/appuser/instance" \
    -e TZ=America/Denver \
    --entrypoint=mirror-config \
    "genericmoniker/mirror:main" \
    ${@}

# Note that args to mirror-config go after all the `docker run` args.
