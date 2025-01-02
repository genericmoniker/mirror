# mirror

Smart/Magic Mirror

![Mirror](./mirror.jpg)

Note: I'm not currently seeking extensive contributions on this project, mainly
because I want to be free to significantly change how it works without
supporting an installed base, but feel free to use it if it seems interesting to
you.

## Raspberry Pi Setup

Using Raspberry Pi OS Bookworm on a Pi Model 3 B+

Things we want to accomplish:

1. Rotate the display as needed
2. Hide the mouse cursor
4. Run the mirror application under Docker
5. Run a browser pointed at the application
6. Turn off the display at times (optional)
7. Automatically update the mirror application when it changes

Start by copying all the files in the "system" directory of this repo to the Pi,
such as with:

```
scp -pr system pi-hostname-or-ip:mirror/system
```

Those files will be used in subsequent steps.

### Rotate the display

This is probably easiest to do from the desktop, with a mouse attached. Go to
the Raspberry Pi menu > Preferences > Screen Configuration.

Pick your display from the Screens drop-down menu, and choose the Rotation value
you need.

### Hide the mouse cursor

Install the unclutter package:

```
sudo apt-get install unclutter
```

### Run the mirror application

Install Docker following the instructions for Raspbian from the
[documentation](https://docs.docker.com/engine/install/debian),
including adding your user to the `docker` group in the [post install
instructions](https://docs.docker.com/engine/install/linux-postinstall/).

For the first start, or to manually update:

```
~/mirror/system/run.sh
```

To have the container restart when the Pi starts up:

```
mkdir -p ~/.config/systemd/user
cp ~/mirror/system/mirror-server.service ~/.config/systemd/user/
systemctl --user enable mirror-server
```

### Run a browser pointed at the application

This installs an autostart file that will start the browser (and a couple of
other things, like disabling screen blanking and power saving):

```
mkdir -p ~/.config/lxsession/LXDE-pi/
cp ~/mirror/system/autostart ~/.config/lxsession/LXDE-pi/
```

### Turn off the display at times

```
sudo crontab -e
```

Copy desired items from sudo-crontab.txt.


### Automatically update the mirror application when it changes

```
sudo crontab -e
```

Copy the item from crontab.txt.


You'll also need to create a `/home/pi/mirror/instance` directory, and
configure services as described below.

## Mirror Configuration

Widgets can generally appear on the mirror in three zones: left and right, where
all widgets are shown all the time, and bottom, where widgets are rotated to
display them one at a time. The enabled widgets and their zone are configured in
instance/mirror.toml.

```toml
[widgets]
left = ["weather", "activity", "now_playing"]
right = ["clock", "calendars-agenda", "calendars-coming_up", "calendars-countdown"]
bottom = ["word_ptbr", "mail", "positivity"]
```

To do any configuration that plugins might need, run the config utility. This
can be done in a couple of ways:

In the development environment:

```
pdm run config
```

On device, when a Docker image exists:

```
~/mirror/system/config.sh
```

That will prompt you for any settings for all plugins, storing them
well-obfuscated in `instance/mirror.db`. Specific plugins can be configured
using the `--plugins` switch. For example:

```
pdm run config --plugins mail weather
```

Some configuration requires using a web browser (such as to handle OAuth), so
you'll either need to have a keyboard attached to the device, or you can do
configuration on another machine (like a desktop PC) and copy
`instance/mirror.db` and `instance/mirror.key` to the device.

## Plugins

Details about plugins requiring non-trivial configuration are explained below.

### Activity

Fitbit step count for the day.

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
1. Run the mirror config and enter the prompted values. For Authorization code,
   enter the value copied from the URL in the previous step.

Note: The authorization code can only be used once, so if something goes wrong,
you may need to generate a new one and re-run configuration to try again.

### Calendars

Data from your Google Calendar.

You'll first need to set up access to the calendar API. You can do that from
[this page](https://goo.gl/5ao8u2) and clicking on "Enable the API".

Follow the prompts to get a client id json file. You'll need that when running
configure.py.

Scope: .../auth/calendar.events.readonly	View events on all your calendars

Application type: Desktop Application

Running configure.py will also launch your default browser so that you can
authorize the mirror application that you just set up for read-only access to
your Google Calendars.

The agenda shows events for today, and "all-day" events for the next week.
You can filter out some upcoming events with a regular expression. Events whose
summary matches the regular expression are *excluded*.

If you want to have calendar events farther out show up, you can put
"mirror-countdown" in them somewhere (probably the description makes the most
sense).

Calendars named "Dinner" or "Meals" show a special icon in the agenda widget.

### Mail

You can send an email with "Mirror" in the subject (case-insensitive) and have
that appear on the mirror for a week. Usually that makes the most sense rotated
with other bottom widgets. The config utility will ask for IMAP settings. For
example:

```python
IMAP_HOST = 'imap.gmail.com'
IMAP_PORT = 993
IMAP_USERNAME = 'somebody@sample.com'
IMAP_PASSWORD = 'mysecretpassword'
```

If you want to use a Gmail account, you'll need to enable IMAP in the Gmail
settings. Also, it might work best to use two-factor authentication and create
an app password for the mirror.

### Now Playing

Currently playing track from Spotify (requires a Spotify Premium account).

1. Create an app at Spotify's [Developer
   Dashboard](https://developer.spotify.com/dashboard/) following [these
   instructions](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/).
   Use "http://localhost:5050/auth" for the redirect URI.
2. Run `mirror-config --plugins=now_playing` and follow the prompts.

### Weather

Current weather and forecasts using Open Weather Map, and air quality from
AirNow.

Setup for this plugin requires two API keys, which you can get from:

- [Open Weather Map](https://home.openweathermap.org/users/sign_up)
- [AirNow](https://docs.airnowapi.org/account/request/)


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

## Development

The mirror application is built with Python using Starlette and htmx.

Information on the mirror is provided by plugins. A plugin is a data source,
plus one or more widgets that specify how the data is displayed. More
information about developing plugins appears later in this document.

### Setup

Install [pdm](https://pdm.fming.dev/latest/), then:

    pdm install --dev

Run with either:

    pdm run mirror

or

    python3 src/mirror/main.py

The server runs on http://localhost:5000.

### Pre-commit hook

For tests, linting and other checks before commit:

    pdm run pre-commit install

## Plugin development

A typical plugin has this structure:

```
mirror/plugins/my_plugin
    static
        my_plugin.css
        my_plugin.png
    __init__.py
    my_plugin.html
```

- The `static` directory has static assets needed for rendering, if any.
- The `__init__.py` module exposes the plugin interface to the mirror
  application. At minimum, the file must exist, but typically it will also
  expose any of these functions that it needs:
    - `configure_plugin` - Called by the config utility to prompt the user for
      config.
    - `start_plugin` - Called by the main mirror app at startup time.
    - `stop_plugin` - Called by the main mirror app at shutdown time.
- The `my_plugin.html` is the Jinja2 template to render the plugin's main
  widget.

Templates can use `url_for("my_plugin.png")` to reference a file in the plugin's
static directory. This is **not** the same `url_for` provided by Starlette.

By convention, to avoid style conflicts, use #my_plugin scoping on CSS
selectors. For example:

```css
#my_plugin p { color: white; }
```

Return no markup if a widget doesn't have anything to display (for example, the
mail plugin does this is there aren't any emails). Especially with the bottom
zone, the widget is skipped while rotating if there is nothing to show, rather
than being blank for the rotation period.

The mirror application provides some services to plugins via the `PluginContext`
class, such as the ability to read and write persistent config data. A plugin
should call the `PluginContext.widget_updated` when its data has been updated
such that one of its widgets would display differently.

You can look at the existing plugins for examples of how things work, including:

- The `calendars` plugin, which has multiple widgets.
- The `weather` plugin, which has two data sources.
- The `positivity` plugin, which has multiple messages that rotate each time the
  plugin itself is rotated.
