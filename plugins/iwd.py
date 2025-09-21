"""Plugin to show network connection changes from iwd."""
from main import PluginContext

# D-Bus constants
IWD_BUS_NAME = "net.connman.iwd"
STATION_INTERFACE = "net.connman.iwd.Station"
OBJ_MANAGER_INTERFACE = "org.freedesktop.DBus.ObjectManager"

# Notification ID for replacement
NOTIFICATION_ID = "iwd_notification_789789"

class Plugin:
    def __init__(self, context: PluginContext):
        self.ctx = context
        self.bus = context.system_bus  # iwd is on the system bus
        self.subscriptions = {}
        # --- Configuration ---
        self.connected_icon = self.ctx.get_config("connected_icon", fallback="network-wireless")
        self.disconnected_icon = self.ctx.get_config("disconnected_icon", fallback="network-wireless-offline")

        self.ctx.log("Initializing iwd plugin...")
        self.setup_iwd_signals()

    def setup_iwd_signals(self):
        """Finds iwd stations and sets up signal handlers using the ObjectManager."""
        try:
            # Get the object manager for iwd to dynamically find stations
            obj_manager_proxy = self.bus.get(IWD_BUS_NAME, "/")
            obj_manager = obj_manager_proxy[OBJ_MANAGER_INTERFACE]

            # Subscribe to signals for when network interfaces are added or removed
            obj_manager.onInterfacesAdded = self.handle_interfaces_added
            obj_manager.onInterfacesRemoved = self.handle_interfaces_removed

            # Process already existing stations
            managed_objects = obj_manager.GetManagedObjects()
            for path, interfaces in managed_objects.items():
                if STATION_INTERFACE in interfaces:
                    self.add_station_listener(path)

            self.ctx.log("Successfully connected to iwd.")
        except Exception as e:
            self.ctx.log(f"Failed to connect to iwd: {e}")

    def add_station_listener(self, path: str):
        """Subscribes to property changes for a given iwd station."""
        if path in self.subscriptions:
            return  # Already listening

        try:
            # We use bus.subscribe for a more robust way to get the signal source
            sub = self.bus.subscribe(
                sender=IWD_BUS_NAME,
                iface='org.freedesktop.DBus.Properties',
                signal='PropertiesChanged',
                object=path,
                signal_fired=self.handle_station_properties_changed
            )
            self.subscriptions[path] = sub
            self.ctx.log(f"Listening for network changes on station: {path}")
        except Exception as e:
            self.ctx.log(f"Error subscribing to station {path}: {e}")

    def remove_station_listener(self, path: str):
        """Unsubscribes from property changes for a station."""
        if path in self.subscriptions:
            self.subscriptions[path].unsubscribe()
            del self.subscriptions[path]
            self.ctx.log(f"Stopped listening on station: {path}")

    def handle_interfaces_added(self, path, interfaces):
        """Handles new D-Bus objects from iwd (e.g., a new WiFi adapter)."""
        if STATION_INTERFACE in interfaces:
            self.ctx.log(f"New station found: {path}")
            self.add_station_listener(path)

    def handle_interfaces_removed(self, path, interfaces):
        """Handles removed D-Bus objects from iwd."""
        if STATION_INTERFACE in interfaces:
            self.ctx.log(f"Station removed: {path}")
            self.remove_station_listener(path)

    def handle_station_properties_changed(self, sender, object_path, iface_name, signal_name, params):
        """Callback for when a station's properties change. This handles connect/disconnect events."""
        interface_name, changed_properties, invalidated_properties = params

        if interface_name != STATION_INTERFACE or 'State' not in changed_properties:
            return

        state = changed_properties['State']
        self.ctx.log(f"Station {object_path} state changed to: {state}")

        if state == 'connected':
            try:
                station_proxy = self.bus.get(IWD_BUS_NAME, object_path)
                network_path = station_proxy.ConnectedNetwork
                if network_path != '/':
                    network_proxy = self.bus.get(IWD_BUS_NAME, network_path)
                    ssid = network_proxy.Name
                    summary = f"Connected to {ssid}"
                    self.ctx.notify(summary=summary, icon=self.connected_icon, replace_id=NOTIFICATION_ID)
            except Exception as e:
                self.ctx.log(f"Error getting network details: {e}")
                self.ctx.notify(summary="Connected to network", icon=self.connected_icon, replace_id=NOTIFICATION_ID)

        elif state == 'disconnected':
            summary = "Network disconnected"
            self.ctx.notify(summary=summary, icon=self.disconnected_icon, replace_id=NOTIFICATION_ID)
