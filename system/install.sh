#!/usr/bin/env bash

# Install the various system components.
# Maybe expand to install Docker?

set -x
set -euo pipefail

# Make the instance directory if it doesn't exist
mkdir -p ~/mirror/instance

# Install the autostart script
mkdir -p ~/.config/lxsession/LXDE-pi/
cp ~/mirror/system/install/autostart ~/.config/lxsession/LXDE-pi/

# Enable lingering (user services w/o the user logged in)
loginctl enable-linger

# Install the mirror service
mkdir -p ~/.config/systemd/user
cp ~/mirror/system/install/mirror-server.service ~/.config/systemd/user/
systemctl --user enable mirror-server

# Install the screen on/off services
cp ~/mirror/system/install/screenon.service  ~/.config/systemd/user/
cp ~/mirror/system/install/screenon.timer    ~/.config/systemd/user/
cp ~/mirror/system/install/screenoff.service ~/.config/systemd/user/
cp ~/mirror/system/install/screenoff.timer   ~/.config/systemd/user/
systemctl --user enable screenon.timer
systemctl --user start  screenon.timer
systemctl --user enable screenoff.timer
systemctl --user start  screenoff.timer

# Install the autoupdate service
cp ~/mirror/system/install/autoupdate.service ~/.config/systemd/user/
cp ~/mirror/system/install/autoupdate.timer   ~/.config/systemd/user/
systemctl --user enable autoupdate.timer
systemctl --user start  autoupdate.timer

# Install the reboot service (requires sudo)
sudo cp ~/mirror/system/install/reboot.service /etc/systemd/system/
sudo cp ~/mirror/system/install/reboot.timer   /etc/systemd/system/
sudo systemctl enable reboot.timer
sudo systemctl start  reboot.timer

# Install unclutter to hide the mouse cursor when it is not being used
sudo apt-get install unclutter -y
