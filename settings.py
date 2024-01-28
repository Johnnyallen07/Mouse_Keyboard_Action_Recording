import configparser
import os
import platform
from datetime import date

CONFIG = configparser.ConfigParser()
VERSION = "1.0.0"
YEAR = date.today().strftime("%Y")

filename = "johnny.cfg"
if platform.system() == "Linux":
    config_location = os.path.join(os.environ.get("HOME"), ".config")
elif platform.system() == "Windows":
    config_location = os.environ.get("APPDATA")
else:
    config_location = os.environ.get("HOME")

config_location = os.path.join(config_location, filename)


def save_config():
    with open(config_location, "w") as config_file:
        CONFIG.write(config_file)


try:
    with open(config_location) as config_file:
        CONFIG.read(config_location)

except:
    CONFIG["DEFAULT"] = {
        "Infinite Playback": False,
        "Repeat Count": 3,
        "Recording Hotkey": 'esc',
        "Playback Hotkey": 'enter',
        "Recording Timer": 3,
        "Force Quit": False,
    }
