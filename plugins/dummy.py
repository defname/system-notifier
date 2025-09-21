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

"""
Dummy plugin to demonstrate the plugin architecture and the capabilities of the
PluginContext.

This plugin is intended as a template and extended documentation for creating
your own plugins. When activated, it performs a series of actions to
demonstrate the various functions of the `ctx` object passed to the constructor.
"""

from gi.repository import GLib
from main import PluginContext
import pydbus

# Unique ID for replaceable notifications.
# Used to update an existing notification instead of creating a new one.
REPLACEABLE_NOTIFICATION_ID = "dummy_plugin_replaceable_notification"

# Unique ID for a notification that will be actively closed.
CLOSABLE_NOTIFICATION_ID = "dummy_plugin_closable_notification"


class Plugin:
    """
    A demonstration plugin class.
    
    When the plugin is initialized, the various methods of the PluginContext
    are called to show how they work.
    """
    def __init__(self, ctx: PluginContext):
        """
        The constructor of the plugin.
        
        The main demonstration logic is executed here.
        
        Args:
            ctx: The PluginContext provided by the main program.
                 It contains all the necessary tools and connections.
        """
        self.ctx = ctx

        # --- 1. Logging ---
        # The log() method allows messages to be printed in the context of the plugin.
        # The tag (e.g., "[dummy]") is automatically prepended.
        self.ctx.log("Plugin is being initialized...")

        # --- 2. Reading Configuration ---
        # get_config() can be used to read values from the plugin's section in
        # config.ini. Here, for example, from a '[dummy]' section.
        # To use this, add the following to your config.ini:
        #
        # [dummy]
        # example_message = This is a test message from the configuration!
        # example_icon = face-smile
        #
        example_message = self.ctx.get_config(
            "example_message",
            fallback="This is a default message (fallback)."
        )
        self.ctx.log(f"Read configuration: 'example_message' = {example_message}")

        # --- 3. Loading Icons ---
        # get_icon() searches for an icon in the configured icon theme,
        # converts it if necessary (e.g., SVG -> PNG), and saves it in the cache.
        # The first parameter is the key in the plugin configuration, the
        # second is a fallback name if the key does not exist.
        info_icon = self.ctx.get_icon("info_icon", fallback="dialog-information")
        example_icon_name = self.ctx.get_config("example_icon", fallback="face-smile")
        example_icon = self.ctx.get_icon("example_icon", fallback=example_icon_name)


        # --- 4. Sending a Simple Notification ---
        # notify() is the central method for sending desktop notifications.
        self.ctx.notify(
            summary="Dummy Plugin Loaded",
            body=example_message,
            icon=example_icon
        )

        # --- 5. Updatable Notification ---
        # A notification with a 'replace_id' can be updated later.
        # Useful for things like volume or brightness changes.
        self.ctx.log("Sending an updatable notification in 3 seconds...")
        GLib.timeout_add_seconds(3, self.show_updatable_notification, info_icon)

        # --- 6. Notification with Progress Bar ---
        self.ctx.log("Sending a notification with a progress bar...")
        self.progress_value = 0
        # We start the update loop for the progress bar
        GLib.timeout_add_seconds(1, self.update_progress_notification)

        # --- 7. Critical, Closable Notification ---
        self.ctx.log("Sending a critical notification that closes after 15s...")
        GLib.timeout_add_seconds(10, self.show_and_close_notification, info_icon)

        # --- 8. D-Bus Interaction ---
        # The PluginContext provides direct access to the system and session bus.
        self.demonstrate_dbus_access()
        
        self.ctx.log("Initialization complete.")

    def show_updatable_notification(self, icon: str) -> bool:
        """Shows a notification that will be updated later."""
        self.ctx.notify(
            summary="Waiting for Update",
            body="This message will be changed in 5 seconds.",
            icon=icon,
            replace_id=REPLACEABLE_NOTIFICATION_ID
        )
        # Call the update method after 5 seconds
        GLib.timeout_add_seconds(5, self.run_notification_update, icon)
        return GLib.SOURCE_REMOVE # Stops the repetition of this timer

    def run_notification_update(self, icon: str) -> bool:
        """Updates the previously sent notification."""
        self.ctx.log("Updating notification...")
        self.ctx.notify(
            summary="Message Updated!",
            body="The content has been successfully changed.",
            icon=icon,
            replace_id=REPLACEABLE_NOTIFICATION_ID # Use the same ID
        )
        return GLib.SOURCE_REMOVE

    def update_progress_notification(self) -> bool:
        """Sends and updates a notification with a progress bar."""
        if self.progress_value > 100:
            self.ctx.log("Progress complete.")
            self.ctx.close_notification("progress_notification")
            return GLib.SOURCE_REMOVE # Stops the timer

        self.ctx.notify(
            summary="Progress Indicator",
            body=f"Value: {self.progress_value}%",
            progress=self.progress_value,
            replace_id="progress_notification"
        )
        self.progress_value += 10
        return GLib.SOURCE_CONTINUE # Continues the timer

    def show_and_close_notification(self, icon: str) -> bool:
        """Shows a critical notification and then actively closes it."""
        self.ctx.notify(
            summary="Critical Warning",
            body="This message will be actively closed in 5 seconds.",
            icon=icon,
            urgency="critical",
            replace_id=CLOSABLE_NOTIFICATION_ID
        )
        GLib.timeout_add_seconds(5, self.close_notification)
        return GLib.SOURCE_REMOVE

    def close_notification(self) -> bool:
        """Calls the close_notification method in the context."""
        self.ctx.log("Actively closing critical notification.")
        self.ctx.close_notification(CLOSABLE_NOTIFICATION_ID)
        return GLib.SOURCE_REMOVE

    def demonstrate_dbus_access(self):
        """Example of accessing D-Bus services."""
        try:
            # --- Session Bus ---
            # Example: Query the owner of the D-Bus service itself.
            session_dbus_proxy = pydbus.SystemBus().get("org.freedesktop.DBus")
            owner = session_dbus_proxy.GetNameOwner("org.freedesktop.DBus")
            self.ctx.log(f"D-Bus session service is owned by: {owner}")

            # --- System Bus ---
            # Example: Query a property from the systemd-logind service.
            system_logind_proxy = self.ctx.system_bus.get(
                "org.freedesktop.login1",           # Service name
                "/org/freedesktop/login1"           # Object path
            )
            # The proxy can be a CompositeObject. We select the correct interface.
            manager_interface = system_logind_proxy["org.freedesktop.login1.Manager"]
            # We read the 'Docked' property as an example, which should exist according
            # to the introspection data.
            is_docked = manager_interface.Docked
            self.ctx.log(f"System is docked (via D-Bus): {is_docked}")

        except Exception as e:
            self.ctx.log(f"Error during D-Bus communication: {e}")