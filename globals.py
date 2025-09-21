import sys

PROG_NAME    = "dbus-notifier"
APP_VERSION      = "0.1"

CONFIG_FILES = ["config.ini", ]
LOG_FILE = sys.stderr
LOG_TAG_WIDTH = 10
DEFAULT_PLUGIN_LIST = "battery, volume_pactl, iwd"

ICON_CACHE_DIR = ".icon_cache"
ICON_THEME_DIR = "/usr/share/icons/breeze"
