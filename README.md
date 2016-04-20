mirror
======

Smart/Magic Mirror 

WARNING: Work-in-progress

Raspberry Pi Setup
------------------

Packages:
* epiphany-browser - display the application
* unclutter - hide the mouse
* xautomate - epiphany full-screen hack

Clone this repo to `~/mirror`.

Copy `autostart` in ~/.config/lxsession/LXDE-pi/autostart

If you want, use the `scroff.sh` and `scron.sh` scripts in a cron job to
schedule when the screen will be off/on. Those need to be run by root.
https://www.raspberrypi.org/documentation/linux/usage/cron.md


Python 3 Setup
--------------

pyvenv ~/.envs/mirror
. ~/.envs/mirror/bin/activate
cd mirror
pip install -r requirements.txt

Create instance/config.py in the mirror directory, with:

    OPENWEATHERMAP_API_KEY = '<your API key here>'

To Do
-----

* Bug showing yesterday's weather forecast
* Would cron work as well for startup? 
  https://www.raspberrypi.org/documentation/linux/usage/cron.md
