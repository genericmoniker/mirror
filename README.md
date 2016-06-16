mirror
======

Smart/Magic Mirror 

WARNING: Work-in-progress

Raspberry Pi Setup
------------------

Packages:

* chromium - display the application
* unclutter - hide the mouse

Tip: Error running chromium, "Failed to load NSS libraries"? Try:

    sudo ln -s /usr/lib/arm-linux-gnueabihf/nss/ /usr/lib/nss

Clone this repo to `~/mirror`.

Copy `autostart` to ~/.config/lxsession/LXDE-pi/autostart

If you want, use the `scroff.sh` and `scron.sh` scripts in a cron job to
schedule when the screen will be off/on. Those need to be run by root.

For example, turn on at 6 AM, off at 11 PM:

    0 6  * * * /home/pi/mirror/scron.sh
    0 23 * * * /home/pi/mirror/scroff.sh

https://www.raspberrypi.org/documentation/linux/usage/cron.md


Python 3 Setup
--------------

    pyvenv ~/.envs/mirror
    . ~/.envs/mirror/bin/activate
    cd mirror
    pip install -r requirements.txt

### Weather ###

Create instance/config.py in the mirror directory, with:

    FORECAST_API_KEY = '<your forecast.io api key here>'
    FORECAST_LOCATION = '<lat>,<long>'

### Agenda ###

Follow [steps a through f here](https://goo.gl/5ao8u2) to get a client 
id json file, but save it as "google_client_id.json" in the instance 
directory.

Then run agenda.py, which will launch your default browser so that you
can authorize the mirror application for read-only access to your 
Google Calendars. This will save google_calendar_creds.json into the
instance directory, which will allow the mirror access. You can do this
on a desktop machine and copy google_calendar_creds.json to your Pi if 
that's easier.

### Tasks ###

Tasks are pulled from Trello cards. There are several items to set in
instance/config.py. First are [API keys](https://trello.com/app-key), 
while the last couple are used to choose which Boards/Lists are
displayed.

TRELLO_API_KEY = '<api key here>'
TRELLO_API_SECRET = '<api secret here>'
TRELLO_TOKEN = '<token here>'
TRELLO_TOKEN_SECRET = '<token secret here>'
TRELLO_BOARD_RE = '<board selection regular expression>'
TRELLO_LIST_RE = '<list selection regular expression>'
