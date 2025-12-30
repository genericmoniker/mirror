#!/usr/bin/env bash

# Install the various system components.

set -x
set -euo pipefail

# Make the instance directory if it doesn't exist
mkdir -p ~/mirror/instance

# Install the autostart desktop file
mkdir -p ~/.config/autostart/
cp ~/mirror/system/install/browser.desktop ~/.config/autostart/

# Enable lingering (user services w/o the user logged in)
loginctl enable-linger

# Install the mirror service
mkdir -p ~/.config/systemd/user
cp ~/mirror/system/install/mirror-server.service ~/.config/systemd/user/
systemctl --user enable --now mirror-server

# Install the screen on/off services
cp ~/mirror/system/install/screenon.service  ~/.config/systemd/user/
cp ~/mirror/system/install/screenon.timer    ~/.config/systemd/user/
cp ~/mirror/system/install/screenoff.service ~/.config/systemd/user/
cp ~/mirror/system/install/screenoff.timer   ~/.config/systemd/user/
systemctl --user enable --now screenon.timer
systemctl --user enable --now screenoff.timer

# Install the autoupdate service
cp ~/mirror/system/install/autoupdate.service ~/.config/systemd/user/
cp ~/mirror/system/install/autoupdate.timer   ~/.config/systemd/user/
systemctl --user enable --now autoupdate.timer

# Install the reboot service (requires sudo)
sudo cp ~/mirror/system/install/reboot.service /etc/systemd/system/
sudo cp ~/mirror/system/install/reboot.timer   /etc/systemd/system/
sudo systemctl enable --now reboot.timer
