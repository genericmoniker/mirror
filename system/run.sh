#!/usr/bin/env bash

# Start the mirror server the first time or update to a newer version.
# If run with -f, force the update and restart even if the image is up to date.

set -euo pipefail

# Check for the force flag
force=false
while getopts "f" opt; do
    case ${opt} in
        f)
            force=true
            ;;
        \?)
            echo "Usage: $0 [-f]"
            exit 1
            ;;
    esac
done


echo "> Pulling latest image"
if docker pull "genericmoniker/mirror:main" | grep "Image is up to date" > /dev/null; then
    echo "> Image is up to date"
    # If the image is up to date and we're not forcing an update, exit.
    if [ "$force" = false ]; then
        echo "> Done"
        exit 0
    fi
fi

echo "> Removing previous container"
docker stop mirror || true && docker rm mirror || true

echo "> Running latest image as a new container"
docker run \
    -d \
    --name="mirror" \
    -p 5000:5000 \
    --restart=always \
    --volume="/home/${USER}/mirror/instance:/home/appuser/instance" \
    -e TZ=America/Denver \
    "genericmoniker/mirror:main"

echo "> Removing dangling images"
dangling_images=$(docker images -q -f 'dangling=true')
if [ -n "$dangling_images" ]; then
    docker image rm $dangling_images
fi

echo "> Refreshing the browser"
until $(curl --output /dev/null --silent --head --fail http://localhost:5000/ready); do
    printf '.'
    sleep 1
done
export DISPLAY=:0.0
export XAUTHORITY=/home/${USER}/.Xauthority
xdotool key --window $(xdotool getactivewindow) ctrl+shift+R
echo

echo "> Done"
