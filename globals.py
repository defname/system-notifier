# This file is part of system-notifier.
#
# system-notifier is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# system-notifier is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with system-notifier.  If not, see <http://www.gnu.org/licenses/>.

import sys

PROG_NAME    = "system-notifier"
APP_VERSION      = "0.1"

CONFIG_FILES = ["config.ini", "~/.config/system-notifier/config.ini"]
LOG_FILE = sys.stderr
LOG_TAG_WIDTH = 10
DEFAULT_PLUGIN_LIST = "battery, volume_pactl, iwd"

ICON_CACHE_DIR = ".icon_cache"
ICON_THEME_DIR = "/usr/share/icons/breeze"