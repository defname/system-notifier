
"""
Plugin to show volume notifications.
Every attempt to use DBus failed, so it works with pactl instead...
"""

import re
import subprocess
import os
from gi.repository import GLib
from main import PluginContext

# fallback configuration
VOLUME_HIGH_ICON = "audio-volume-high"
VOLUME_MEDIUM_ICON = "audio-volume-medium"
VOLUME_LOW_ICON = "audio-volume-low"
VOLUME_MUTED_ICON = "audio-volume-muted"
NOTIFICATION_ID = "volume_notification_12345"

# for consitent output of pactl
ENV=os.environ.copy()
ENV["LANG"] = "en_US.UTF-8"

class Plugin:
    def __init__(self, ctx: PluginContext):
        self.ctx = ctx
        self.high_icon = self.ctx.get_icon("high_icon", fallback=VOLUME_HIGH_ICON)
        self.mid_icon = self.ctx.get_icon("medium_icon", fallback=VOLUME_MEDIUM_ICON)
        self.low_icon = self.ctx.get_icon("low_icon", fallback=VOLUME_LOW_ICON)
        self.muted_icon = self.ctx.get_icon("muted_icon", fallback=VOLUME_MUTED_ICON)
        self.last_volume = 0

        self.default_sink_idx = self.get_default_sink_index()

        try:
            # Start pactl subscribe and watch its output
            pactl_process = subprocess.Popen(["pactl", "subscribe"], stdout=subprocess.PIPE, text=True, env=ENV)
            GLib.io_add_watch(pactl_process.stdout, GLib.IO_IN, self.on_pactl_event)
            self.ctx.log("Subscribed to pactl events")
        except FileNotFoundError:
            self.ctx.log("pactl command not found. This plugin will not work.")
        except Exception as e:
            self.ctx.log(f"Error starting pactl subscribe: {e}")

    def on_pactl_event(self, stream, condition):
        line = stream.readline()
        if line and f"Event 'change' on sink #{self.default_sink_idx}" == line.strip():
            print(line)
            self.ctx.log("Sink event detected")
            self.update_volume_notification()
        return True  # Keep the watch active

    def get_default_sink_index(self):
        # Default-Sink-Namen ermitteln
        sink_name = subprocess.check_output(
            ["pactl", "get-default-sink"],
            text=True
        ).strip()

        # Alle Sinks listen und Index zum Namen suchen
        sinks = subprocess.check_output(
            ["pactl", "list", "sinks", "short"],
            text=True
        ).splitlines()

        for line in sinks:
            idx, name, *_ = line.split()
            if name == sink_name:
                return int(idx)
        return None

    def update_volume_notification(self):
        try:
            # Get volume and mute status
            volume_str = subprocess.check_output(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], text=True, env=ENV)
            mute_str = subprocess.check_output(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], text=True, env=ENV)

            is_muted = "yes" in mute_str.lower()

            if is_muted:
                self.ctx.notify("Volume", "Muted", icon=self.muted_icon, replace_id=NOTIFICATION_ID)
                self.last_volume = 0
                return

            # Extract volume percentage using regex
            match = re.search(r'(\d+)%', volume_str)
            if match:
                volume = int(match.group(1))
                if volume == self.last_volume:
                    return
                self.last_volume = volume

                icon = self.high_icon if volume >= 75 else self.mid_icon if volume >= 35 else self.low_icon
                self.ctx.notify(f"Volume: {volume}%", "", icon=icon, replace_id=NOTIFICATION_ID, progress=volume)
            else:
                # Fallback if regex fails
                self.ctx.log(f"Could not parse volume: {volume_str}")
                self.ctx.notify("Volume", volume_str.strip(), icon=self.high_icon, replace_id=NOTIFICATION_ID, progress=volume)

        except FileNotFoundError:
            self.ctx.log("pactl command not found.")
        except Exception as e:
            self.ctx.log(f"Error updating volume notification: {e}")

