#!/usr/bin/python3

import libevdev
import sys
from pydbus import SessionBus
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/tmp/ppso.log"),
        logging.StreamHandler()
    ]
)

# Screen state (on/off)
state = True

sessionBus = SessionBus()

inputDbus = sessionBus.get("org.kde.KWin", "/org/kde/KWin/InputDevice/event1")
powerdevilDbus = sessionBus.get("org.kde.KWin", "/component/org_kde_powerdevil")

fd = open('/dev/input/event0', 'rb')
d = libevdev.Device(fd)
if not d.has(libevdev.EV_KEY.KEY_POWER):
     print('This does not look like a power button thing device')
     sys.exit(0)

logging.info("Waiting for events now...")

# Loop indefinitely while pulling the currently available events off
# the file descriptor
while True:
    for e in d.events():
        if not e.matches(libevdev.EV_KEY):
            continue

        # KEY_POWER release
        if e.matches(libevdev.EV_KEY.KEY_POWER) and e.value == 0:
            state = not state
            if state:
                logging.info("Enabling screen...")
                # Enable input device again
                # Screen gets woken up by some other component
                inputDbus.enabled = True
            else:
                logging.info("Disable screen...")
                # Disable input device
                inputDbus.enabled = False
                # Turn off screen
                powerdevilDbus.invokeShortcut("Turn Off Screen")

