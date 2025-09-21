""" Plugin to show brightness notifications using D-Bus. """

import os
from main import PluginContext
import pydbus

# fallback configuration
BRIGHTNESS_HIGH_ICON = "display-brightness-high-symbolic"
BRIGHTNESS_MEDIUM_ICON = "display-brightness-medium-symbolic"
BRIGHTNESS_LOW_ICON = "display-brightness-low-symbolic"
NOTIFICATION_ID = "brightness_notification_12345"

class Plugin:
    def __init__(self, ctx: PluginContext):
        self.ctx = ctx
        self.high_icon = self.ctx.get_icon("high_icon", fallback=BRIGHTNESS_HIGH_ICON)
        self.mid_icon = self.ctx.get_icon("medium_icon", fallback=BRIGHTNESS_MEDIUM_ICON)
        self.low_icon = self.ctx.get_icon("low_icon", fallback=BRIGHTNESS_LOW_ICON)

        try:
            pydbus.SystemBus().subscribe(
                iface="org.freedesktop.DBus.Properties",
                signal="PropertiesChanged",
                signal_fired=self.on_properties_changed
            )
            self.ctx.log("Subscribed to D-Bus brightness events.")
        except Exception as e:
            self.ctx.log(f"Error subscribing to D-Bus brightness events: {e}")

    def on_properties_changed(self, sender, object_path, iface, signal, params):
        interface_name, changed_properties, invalidated_properties = params
        if "backlight" in object_path and "SysFSPath" in changed_properties:
            self.ctx.log("Brightness change event detected.")
            self.update_brightness_notification(sysfs_path=changed_properties["SysFSPath"])

    def update_brightness_notification(self, sysfs_path=None):
        try:
            if sysfs_path is None:
                # Find the backlight device if not provided
                for device in os.listdir("/sys/class/backlight/"):
                    sysfs_path = os.path.join("/sys/class/backlight", device)
                    break
            
            if sysfs_path:
                with open(os.path.join(sysfs_path, "actual_brightness")) as f:
                    brightness = int(f.read())
                with open(os.path.join(sysfs_path, "max_brightness")) as f:
                    max_brightness = int(f.read())
                
                brightness_percent = int((brightness / max_brightness) * 100)

                icon = self.high_icon if brightness_percent >= 75 else self.mid_icon if brightness_percent >= 35 else self.low_icon
                self.ctx.notify(f"Brightness: {brightness_percent}%", "", icon=icon, replace_id=NOTIFICATION_ID, progress=brightness_percent)
            else:
                self.ctx.log("No backlight device found.")

        except Exception as e:
            self.ctx.log(f"Error updating brightness notification: {e}")