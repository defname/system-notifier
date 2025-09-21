from globals import DEFAULT_PLUGIN_LIST, ICON_CACHE_DIR, ICON_THEME_DIR
from utils.helper import log
from utils.icon_loader import get_icon

from typing import Literal
import importlib
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Notify", "0.7")
from gi.repository import Notify
from gi.repository import GLib



class PluginContext:
    """A container for shared ressources passed to each plugin."""
    def __init__(self, plugin_name, config):
        self.config = config
        self.plugin = plugin_name

        self.cache_dir = self.config.get("main", "cache_dir", fallback=ICON_CACHE_DIR)
        self.theme_dir = self.config.get("main", "icon_theme_dir", fallback=ICON_THEME_DIR)

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

    def get_icon(self, config_key: str, fallback: str):
        """
        Gets the icon name from the cofig or from the fallback.
        Searches the theme and converts the icon if necessary.
        """
        final_name = self.get_config(config_key, fallback=fallback)
        return get_icon(final_name, self.theme_dir, self.cache_dir)

def load_plugins(config, plugin_list=""):
    """Loads all enabled plugins from the 'plugins' directory."""
    enabled_plugins = ""
    if plugin_list:
        enabled_plugins = [p.strip() for p in plugin_list.split(",")]
    else:
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
                context = PluginContext(plugin_name, config)
                plugin_instance = module.Plugin(context)
                loaded_plugins.append(plugin_instance)
                log("Plugin loaded", tag=plugin_name)
        except Exception as e:
            log(f"Error while loading plugin: {e}", tag=plugin_name)
    return loaded_plugins