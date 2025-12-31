#! /bin/bash

# Check for updates by comparing the current git hash with the latest git hash
# on the main branch. If there is a difference, update the system.

set -euo pipefail

# Log all output
exec 1> >(logger --tag called-update --priority user.info)
exec 2> >(logger --tag called-update --priority user.error)

echo "Starting update check..."

# Run from this script's parent directory
cd "$(dirname "$0")/.."

current_hash=$(git rev-parse main)
latest_hash=$(git ls-remote origin -h refs/heads/main | cut -f1)

if [ "$current_hash" != "$latest_hash" ]; then
    echo "Application update available. Updating to commit hash ${latest_hash}..."
    git pull || { echo "Failed to pull latest changes"; exit 1; }
    ./install.sh || { echo "Failed to run install script"; exit 1; }
    echo "Application updated."
else
    echo "Application is up to date at commit hash ${current_hash}."
fi
