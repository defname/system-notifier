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

PROG_NAME    = "dbus-notifier"
APP_VERSION      = "0.1"

CONFIG_FILES = ["config.ini", ]
LOG_FILE = sys.stderr
LOG_TAG_WIDTH = 10
DEFAULT_PLUGIN_LIST = "battery, volume, iwd"


def log(*args, tag="main", **kwargs):
    """Helper for log messages"""
    print(f"{"[" + tag + "]":{LOG_TAG_WIDTH}}", *args, file=LOG_FILE, **kwargs)


class PluginContext:
    """A container for shared ressources passed to each plugin."""
    def __init__(self, plugin_name, config, system_bus: pydbus.SystemBus, session_bus: pydbus.SessionBus):
        self.config = config
        self.plugin = plugin_name
        self.system_bus = system_bus
        self.session_bus = session_bus

        global_timeout = self.config.get("main", "timeout", fallback=0)
        self.notification_timeout = int(self.get_config("timeout", fallback=global_timeout))
        
        self.active_notifications = {}
    
    def log(self, *args, **kwargs):
        """Helper for log messages"""
        log(*args, tag=self.plugin, **kwargs)
    
    def get_config(self, option, fallback=None):
        """Read a value from the plugin's config."""
        return self.config.get(self.plugin, option, fallback=fallback)
    
    def notify(self,
               summary: str,
               body: str = "",
               icon: str = "",
               urgency: Literal["low", "normal", "critical"] = "normal",
               timeout: int = None,
               replace_id: str = None,
               progress: int = None):
        """Send a desktop notification"""
        urgency_map = {
            "low": Notify.Urgency.LOW,
            "normal": Notify.Urgency.NORMAL,
            "critical": Notify.Urgency.CRITICAL,
        }

        notification_to_show = None
        if replace_id and replace_id in self.active_notifications:
            notification_to_show = self.active_notifications[replace_id]
            notification_to_show.update(summary, body, icon)
        else:
            notification_to_show = Notify.Notification.new(summary, body, icon)

        notification_to_show.set_urgency(urgency_map.get(urgency, "normal"))
        notification_to_show.set_timeout(timeout if timeout is not None
                                         else self.notification_timeout)
        if progress is not None:
            notification_to_show.set_hint("value", GLib.Variant.new_int32(progress))

        notification_to_show.show()

        if replace_id:
            self.active_notifications[replace_id] = notification_to_show

    def close_notification(self, replace_id: str):
        """Actively close a notification"""
        if replace_id in self.active_notifications:
            self.active_notifications[replace_id].close()
            del self.active_notifications[replace_id]


def load_plugins(config, system_bus, session_bus):
    """Loads all enabled plugins from the 'plugins' directory."""
    enabled_plugins = [p.strip() for p
                       in config.get("main", "enabled_plugins", fallback=DEFAULT_PLUGIN_LIST)
                                .split(",") if p.strip()]
    log(f"Enabled plugins: {', '.join(enabled_plugins) if enabled_plugins else 'None'}")

    loaded_plugins = []
    for plugin_name in enabled_plugins:
        module_name = f"plugins.{plugin_name}"
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, 'Plugin'):
                context = PluginContext(plugin_name, config, system_bus, session_bus)
                plugin_instance = module.Plugin(context)
                loaded_plugins.append(plugin_instance)
                log("Plugin loaded", tag=plugin_name)
        except Exception as e:
            log(f"Error while loading plugin: {e}", tag=plugin_name)
    return loaded_plugins

def init_argparse():
    """Initialize the argument parser."""
    parser = argparse.ArgumentParser(
        prog=PROG_NAME,
        description="A simple system event monitor and notifier.",
        epilog=f"Version {APP_VERSION}"
    )
    parser.add_argument("--config", "-c", type=str, default=None, help="specify a config file")
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
    loaded_plugins = load_plugins(config, system_bus, session_bus)

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

