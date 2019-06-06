mirror
======

Smart/Magic Mirror 

WARNING: Work-in-progress; meets my needs but isn't fully generalized.

Raspberry Pi Setup
------------------

Using Raspbian Stretch.

Install the unclutter package for hiding the mouse cursor.

    sudo apt-get install unclutter

You might want to rotate the display if your monitor is hung vertically. Edit
/boot/config.txt:

    sudo nano /boot/config.txt

Add a line to the end of the file:

    display_rotate=3

The value indicates the orientation:

| Value  | Orientation |
|---|---------------|
| 0 | Normal |
| 1 | 90 degrees |
| 2 | 180 degrees |
| 3 | 270 degrees |

Clone this repo to `~/mirror`.

Copy the mirror-server systemd service unit file and enable it:

    sudo cp ~/mirror/system/mirror-server.service /etc/systemd/system/
    sudo systemctl enable mirror-server

Make a backup of your autostart file (just in case):

    cp ~/.config/lxsession/LXDE-pi/autostart ~/.config/lxsession/LXDE-pi/autostart.bak

Copy the `autostart` file from the project:

    cp ~/mirror/system/autostart ~/.config/lxsession/LXDE-pi/autostart

If you want, use the `scroff.sh` and `scron.sh` scripts in a cron job to
schedule when the screen will be off/on. Those need to be run by root. To edit
cron jobs, run:

    sudo crontab -e

For example, turn on at 5:50 AM, off at 11 PM, add these lines:

    50 5  * * * /home/pi/mirror/system/scron.sh
    0 23  * * * /home/pi/mirror/system/scroff.sh

https://www.raspberrypi.org/documentation/linux/usage/cron.md

You'll also need to create an `instance` directory, and configure
services as described below.


Python 3.5 Setup
----------------

```bash
sudo apt-get update
sudo apt-get install libffi-dev libssl-dev
python3 -m venv ~/.envs/mirror
. ~/.envs/mirror/bin/activate
cd mirror
pip install wheel
pip install -r requirements.txt
```

For configuring other services, you'll need to create `instance/config.py` in
the mirror directory, with contents described below.

### Sentry Logging ###

You can get a free "hobbyist" account at https://sentry.io. This will let you
get alerts if something goes wrong in the application.

Then add a SENTRY_CONFIG dictionary to `instance/config.py` like that shown in
the [documentation](https://docs.sentry.io/clients/python/integrations/flask/).

### Weather ###

Add these values to `instance/config.py`:

```py
FORECAST_API_KEY = '<your forecast.io api key here>'
FORECAST_LOCATION = '<lat>,<long>'
```

### Worth ###

If you use [Personal Capital](https://www.personalcapital.com/), you can set up
the mirror to show a simplified graph of "net worth". This is just the total of
cash accounts minus the total of credit accounts, to give a quick spending 
metric. The value is shown rounded to the nearest $1000, and doesn't actually
show a dollar sign anywhere.

To set it up, run:
```bash
~/.envs/mirror/bin/python3 mirrorapp.py --setup 
```
It will prompt you for your username and password, and will go through the
two-factor process (send an SMS to your registered phone number).

Your credentials are stored in a well-obfuscated form in `instance/mirror.db`.

### Agenda ###

Follow [steps a through f here](https://goo.gl/5ao8u2) to get a client 
id json file, but save it as "google_client_id.json" in the `instance` 
directory.

Then run agenda.py, which will launch your default browser so that you
can authorize the mirror application for read-only access to your 
Google Calendars. This will save google_calendar_creds.json into the
`instance` directory, which will allow the mirror access. You can do this
on a desktop machine and copy google_calendar_creds.json to your Pi if 
that's easier.

The agenda shows events for today, and "all-day" events for the next few days.
If you want to have events farther out show up, you can put "mirror-countdown"
in them somewhere (probably the description makes the most sense).

### Emails ###

You can send an email with "Mirror" in the subject (case-insensitive) and have
that appear on the mirror for a week, rotated with other bottom-half messages.
To do that, you need to configure mail settings in the config file:

```py
IMAP_HOST = 'imap.gmail.com'
IMAP_PORT = 993
IMAP_USERNAME = 'somebody@sample.com'
IMAP_PASSWORD = 'mysecretpassword'
```
If you want to use a Gmail account, you'll need to enable IMAP in the settings.
Also, it might work best to use two-factor authentication and create an app
password.

### Tasks ###

(Currently disabled)

Tasks are pulled from Trello cards. There are several items to set in
instance/config.py. First are [API keys](https://trello.com/app-key), 
while the last couple are used to choose which Boards/Lists are
displayed.

```py
TRELLO_API_KEY = '<api key here>'
TRELLO_API_SECRET = '<api secret here>'
TRELLO_TOKEN = '<token here>'
TRELLO_TOKEN_SECRET = '<token secret here>'
TRELLO_BOARD_RE = '<board selection regular expression>'
TRELLO_LIST_RE = '<list selection regular expression>'
```

Troubleshooting
---------------

If the browser doesn't show the right data when starting the Pi, it's likely
that the Python application had an exception while starting. You can check that
by ssh into the Pi and running:

    sudo systemctl status mirror-server

If you want to run the application stand-alone:

```bash
cd ~/mirror
~/.envs/mirror/bin/python3 mirrorapp.py
```
