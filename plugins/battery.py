"""Plugin to show power supply and battery notifications."""

from main import PluginContext

# fallback configuration
ON_MESSAGE = "Netzteil angeschlossen"
OFF_MESSAGE = "Netzteil getrennt"
ON_ICON = "ac-adapter"
OFF_ICON = "battery-full"

LOW_MESSAGE = "Akkustand ist niedrig"
CRITICAL_MESSAGE = "Akkustand ist kritisch!"
LOW_ICON = "battery-low"
CRITICAL_ICON = "battery-caution"

# notification id for notification replacement (just some random but unique string)
NOTFICATION_ID = "battery_notifications_1231231"

# UPower constants
DEVICE_TYPE_LINE_POWER = 1
DEVICE_TYPE_BATTERY    = 2
WARNING_LEVEL_LOW      = 3
WARNING_LEVEL_CRITICAL = 4


class Plugin:
    def __init__(self, ctx: PluginContext):
        self.ctx = ctx

        self.bus = ctx.system_bus

        self.messages = {
            "on": self.ctx.get_config("on_message", fallback=ON_MESSAGE),
            "off": self.ctx.get_config("off_message", fallback=OFF_MESSAGE),
            "low": self.ctx.get_config("low_message", fallback=LOW_MESSAGE),
            "critical": self.ctx.get_config("critical_message", fallback=CRITICAL_MESSAGE),
        }

        self.icons = {
            "on": self.ctx.get_icon("on_icon", fallback=ON_ICON),
            "off": self.ctx.get_icon("off_icon", fallback=OFF_ICON),
            "low": self.ctx.get_icon("low_icon", fallback=LOW_ICON),
            "critical": self.ctx.get_icon("critical_icon", fallback=CRITICAL_ICON),
        }

        self.find_devices_and_setup_signals()

    def find_devices_and_setup_signals(self):
        """Find power supply and battery devices."""
        try:
            # choose proxy and interface
            upower = self.bus.get("org.freedesktop.UPower")

            # find the correct devices
            for device_path in upower.EnumerateDevices():
                device = self.bus.get("org.freedesktop.UPower", device_path)
                device_type = device.Type

                if device_type == DEVICE_TYPE_LINE_POWER: # Line Power
                    self.ctx.log(f"Power device found: {device_path}")
                    device.onPropertiesChanged = self.handle_line_power_change
                elif device_type == DEVICE_TYPE_BATTERY: # Battery
                    self.ctx.log(f"Battery found: {device_path}")
                    device.onPropertiesChanged = self.handle_battery_change

        except Exception as e:
            self.ctx.log(f"Connection to UPower failed: {e}")

    def handle_line_power_change(self, interface_name, changed_properties, invalidated_properties):
        """Handle power supply signals."""
        if 'Online' in changed_properties:
            if changed_properties['Online']:
                self.ctx.notify(self.messages["on"],
                                icon=self.icons["on"],
                                replace_id=NOTFICATION_ID)
            else:
                self.ctx.notify(self.messages["off"],
                                icon=self.icons["off"],
                                replace_id=NOTFICATION_ID)

    def handle_battery_change(self, interface_name, changed_properties, invalidated_properties):
        """Handle battery signals."""
        if 'WarningLevel' in changed_properties:
            level = changed_properties['WarningLevel']
            # UPower WarningLevel enum: 0-2=OK, 3=Low, 4=Critical
            if level == WARNING_LEVEL_LOW:
                self.ctx.notify(self.messages["low"],
                                icon=self.icons["low"],
                                urgency="low",
                                replace_id=NOTFICATION_ID)
            elif level == WARNING_LEVEL_CRITICAL:
                self.ctx.notify(self.messages["critical"],
                                icon=self.icons["critical"],
                                urgency="critical",
                                replace_id=NOTFICATION_ID)
