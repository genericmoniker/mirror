# mirror

Smart/Magic Mirror

WARNING: Work-in-progress; meets my needs but isn't fully generalized.

WARNING: This document is not fully up-to-date.

## Raspberry Pi Setup

Using Raspberry Pi OS.

It will probably be helpful to enable ssh access, which can be done following
the [Remote Access
instructions](https://www.raspberrypi.org/documentation/computers/remote-access.html).

Install the unclutter package for hiding the mouse cursor, and the xdotool to
make it easier to refresh the browser from the command line.

    sudo apt-get install unclutter xdotool

You might want to rotate the display if your monitor is hung vertically. Edit
/boot/config.txt:

    sudo nano /boot/config.txt

Add a line to the end of the file:

    display_rotate=3

The value indicates the orientation:

| Value | Orientation |
| ----- | ----------- |
| 0     | Normal      |
| 1     | 90 degrees  |
| 2     | 180 degrees |
| 3     | 270 degrees |

Install docker following the instructions for Raspbian from the
[documentation](https://docs.docker.com/engine/install/debian/#install-using-the-convenience-script),
including adding your user to the `docker` group in the [post install
instructions](https://docs.docker.com/engine/install/linux-postinstall/).

Copy the mirror-server.service systemd service unit file from this repo and
enable it:

    sudo cp ~/mirror/system/mirror-server.service /etc/systemd/system/
    sudo systemctl enable mirror-server

Make a backup of your autostart file (just in case):

    sudo cp /etc/xdg/lxsession/LXDE-pi/autostart /etc/xdg/lxsession/LXDE-pi/autostart.bak

Copy the `autostart` file from the project:

    sudo cp ~/mirror/system/autostart /etc/xdg/lxsession/LXDE-pi/autostart

If you want, use the `scroff.sh` and `scron.sh` scripts in a cron job to
schedule when the screen will be off/on. Those need to be run by root. To edit
cron jobs, run:

    sudo crontab -e

For example, turn on at 5:45 AM, off at 11 PM, add these lines:

    45 5  * * * /home/pi/mirror/system/scron.sh
    0 23  * * * /home/pi/mirror/system/scroff.sh

https://www.raspberrypi.org/documentation/linux/usage/cron.md

You'll also need to create a `/home/pi/mirror/instance` directory, and
configure services as described below.

## Mirror Configuration

To do any configuration that plugins might need, run:

```
~/mirror/system/mirror-config
```

That will prompt you for any settings, storing them well-obfuscated in
`instance/mirror.db`.

Some configuration requires using a web browser, so you'll either need to have
a keyboard attached to the device, or you can do configuration on another
machine (like a desktop PC) and copy `instance/mirror.db` and
`instance/mirror.key` to the device.

## Plugins

### Activity

Fitbit step count for the data.

1. Go to https://dev.fitbit.com/apps, logging in with your Fitbit account.
1. Click on "Register a new app"
1. Fill in the requested data. Most of the values before "OAuth 2.0 Application
   Type" will be used for the authorization prompt, so the values don't matter
   much.
1. For "OAuth 2.0 Application Type" choose "Personal"
1. For "Redirect URL" enter "http://localhost:5000/fitbit"
1. For "Default Access Type" choose "Read-Only"
1. After agreeing to terms, click "Register"
1. When that succeeds, click the "OAuth 2.0 tutorial page" link
1. For "Flow type" choose "Authorization Code Flow"
1. For "Select Scopes" check "activity"
1. There is a link below text saying, "We've generated the authorization URL
   for you, all you need to do is just click on link below:" Click it.
1. Your browser will go to the callback URL entered earlier (likely displaying
   an error), and will have a `code` query parameter like
   `?code=7b64c4b088b9c841d15bcac15d4aa7433d35af3e#_=`. Copy the
   `7b64c4b088b9c841d15bcac15d4aa7433d35af3e` part.
1. Run mirror-config, and enter the prompted values. For Authorization code,
   enter the value copied from the URL in the previous step.

Note: The authorization code can only be used once, so if something goes wrong, you may
need to generate a new one and re-run configuration to try again.

### Calendar

Data from your Google Calendar.

You'll first need to set up access to the calendar API. You can do that from
[this page](https://goo.gl/5ao8u2) and clicking on "Enable the Google Calendar
API".

Follow the prompts to get a client id json file. You'll need that when running
configure.py.

Running configure.py will also launch your default browser so that you can
authorize the mirror application that you just set up for read-only access to
your Google Calendars.

The agenda shows events for today, and "all-day" events for the next week.
You can filter out some upcoming events with a regular expression. Events whose
summary matches the regular expression are *excluded*.

If you want to have calendar events farther out show up, you can put
"mirror-countdown" in them somewhere (probably the description makes the most
sense).

### Emails

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

### Now Playing

Currently playing track from Spotify (requires a Spotify Premium account).

1. Create an app at Spotify's [Developer
   Dashboard](https://developer.spotify.com/dashboard/) following [these
   instructions](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/).
   Use "http://localhost:5050/auth" for the redirect URI.
2. Run `mirror-config --plugins=now_playing` and follow the prompts.

### Weather

Current weather and forecasts using Open Weather Map.

### Worth

If you use [Personal Capital](https://www.personalcapital.com/), you can set up
the mirror to show a simplified graph of "net worth". This is just the total of
cash accounts minus the total of credit accounts, to give a quick spending
metric. The value is shown rounded to the nearest $1000, and doesn't actually
show a dollar sign anywhere.

Configuration will prompt you for your username and password, and will go
through the two-factor process (send an SMS to your registered phone number).

Your credentials are stored in a well-obfuscated form in `instance/mirror.db`.

### Tasks

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

## Sentry Logging

You can get a free "hobbyist" account at https://sentry.io. This will let you
get alerts if something goes wrong in the application.

Then add a SENTRY_CONFIG dictionary to `instance/config.py` like that shown in
the [documentation](https://docs.sentry.io/clients/python/integrations/flask/).

## Troubleshooting

If the browser doesn't show the right data when starting the Pi, it's likely
that the Python application had an exception while starting. You can check that
by ssh into the Pi and running:

    systemctl status mirror-server

Or, to see more logs:

    journalctl -u mirror-server

If you want to run the application stand-alone:

```bash
cd ~/mirror
~/.envs/mirror/bin/python3 mirrorapp.py
```

## Development

The mirror application has two main parts:

1. The backend, developed with Python using starlette
2. The frontend, developed with JavaScript using svelte

### Backend

Install [pdm](https://pdm.fming.dev/latest/), then:

    pdm install --dev

Run the backend with either:

    pdm run mirror

or

    python3 backend/src/mirror/main.py

The server runs on http://localhost:5000, but you'll need to have built the
frontend to get a UI.

### Frontend

Run the backend first!

1. Install [npm](https://www.npmjs.com/get-npm).
2. Then cd to the `frontend` directory and run `npm install`
3. Run `npm run dev`

The application will be available on http://localhost:5001, with hot-reload.

You can also:

    npm run build

To build the production frontend.

### Pre-commit hook

For tests, linting and other checks before commit:

    pdm run pre-commit install
