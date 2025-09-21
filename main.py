#!/usr/bin/env python3

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
import configparser
import argparse
from dbus.mainloop.glib import DBusGMainLoop
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")
from gi.repository import GLib, Notify

from globals import APP_VERSION, PROG_NAME, CONFIG_FILES, LOG_FILE
from utils.helper import log
from utils.plugin_loader import PluginContext, load_plugins


def init_argparse():
    """Initialize the argument parser."""
    parser = argparse.ArgumentParser(
        prog=PROG_NAME,
        description="A simple system event monitor and notifier.",
        epilog=f"Version {APP_VERSION}"
    )
    parser.add_argument("--config", "-c", type=str, default=None, help="specify a config file")
    parser.add_argument("--plugins", "-p", type=str, default="", help="give a list of plugins to load. If set the enabled_plugins option in the config file will be ignored.")
    return parser

def load_config(config_file: str):
    config = configparser.ConfigParser()
    loaded_files: list[str]
    if config_file:
        loaded_files = config.read(config_file)
        if not loaded_files:
            log(f"Config file {config_file} not found.")
            sys.exit(1)
    else:
        loaded_files = config.read(CONFIG_FILES)
        if not loaded_files:
            log("No configuration files found.")
    return config

def main():
    """Global entry point"""
    # command line argumnts
    argparser = init_argparse()
    args = argparser.parse_args()

    # load config
    config = load_config(args.config)

    # GLib Main Loop
    DBusGMainLoop(set_as_default=True)

    # init libnotify
    Notify.init(PROG_NAME)

    # available_plugin_files = [f for f in os.listdir(plugin_dir) if f.endswith(".py") and not f.startswith("__")]
    loaded_plugins = load_plugins(config, plugin_list=args.plugins)

    if not loaded_plugins:
        log("No plugins loaded. Exiting.")
        return

    log("Listen for system events... (Cancel with Ctrl+C)")
    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        print(file=LOG_FILE)
        log("Goodby =)")
    finally:
        Notify.uninit()


if __name__ == "__main__":
    main()