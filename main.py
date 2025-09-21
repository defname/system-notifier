#!/usr/bin/env python3

import importlib
import sys
import configparser
import argparse
from typing import Literal
import pydbus
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

def main():
    """Global entry point"""
    # command line argumnts
    argparser = init_argparse()
    try:
        args = argparser.parse_args()
    except argparse.ArgumentError:
        return

    # load config
    config = configparser.ConfigParser()
    loaded_files: list[str]
    if args.config:
        loaded_files = config.read(args.config)
        if not loaded_files:
            log(f"Config file {args.config} not found.")
            return
    else:
        loaded_files = config.read(CONFIG_FILES)
        if not loaded_files:
            log("No configuration files found.")

    # init dbus and GLib Main Loop
    system_bus = pydbus.SystemBus()
    session_bus = pydbus.SessionBus()
    DBusGMainLoop(set_as_default=True)

    # init libnotify
    Notify.init(PROG_NAME)

    # available_plugin_files = [f for f in os.listdir(plugin_dir) if f.endswith(".py") and not f.startswith("__")]
    loaded_plugins = load_plugins(config, system_bus, session_bus, plugin_list=args.plugins)

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

