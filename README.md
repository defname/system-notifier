# System Notifier

A simple and extensible system event monitor for Linux that provides a framework for sending desktop notifications based on various system events.

## Features

*   Monitors system events via D-Bus.
*   Sends desktop notifications for events.
*   Plugin-based architecture to easily add new event listeners.
*   Configuration via an INI file.

## Included Plugins

The project comes with a few plugins:

*   **Battery**: Monitors the power supply and battery status using UPower. It sends notifications for:
    *   AC adapter plugged in/unplugged.
    *   Low battery level.
    *   Critical battery level.
*   **volume_pactl**: Monitors volume changes using the `pactl` command-line tool. It shows a notification with a progress bar when the volume is changed or muted.
*   **iwd**: Monitors network connections using iwd.
*   **brightness**: Monitors screen brightness changes and shows a notification with a progress bar.
*   **Dummy**: A simple boilerplate for creating new plugins.

## Dependencies

The script requires the following:

*   Python 3
*   `pydbus`
*   `PyGObject`
*   `cairosvg`
*   `lxml`
*   GObject introspection bindings for `Notify` (`gir1.2-notify-0.7`)

On a Debian-based system, you can install these with:

```bash
sudo apt-get install python3-gi python3-dbus gir1.2-notify-0.7
```

And the python libraries via pip:
```bash
pip install pydbus cairosvg lxml
```

The `volume_pactl` plugin also requires `pactl`, which is usually included in the `pulseaudio-utils` package:
```bash
sudo apt-get install pulseaudio-utils
```

## Installation

There are two ways to install system-notifier:

### 1. Manual Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/system-notifier.git
    cd system-notifier
    ```
2.  Install the dependencies as described above.

### 2. Using the Install Script (Recommended)

The project includes an installation script that sets up a systemd user service. This will automatically start the notifier when you log in.

1.  Clone the repository (if you haven't already):
    ```bash
    git clone https://github.com/your-username/system-notifier.git
    cd system-notifier
    ```
2.  Run the install script:
    ```bash
    ./install.sh
    ```

The script will:
*   Create a systemd service file in `~/.config/systemd/user/`.
*   Reload the systemd user daemon.
*   Enable and start the `system-notifier.service`.

You can check the status of the service with `systemctl --user status system-notifier.service`.

### Uninstallation

To uninstall the service and remove all related files, run the `uninstall.sh` script:

```bash
./uninstall.sh
```

This will:
*   Stop and disable the systemd service.
*   Remove the service file.
*   Remove the icon cache directory.

## Usage

1.  Create a configuration file named `config.ini` in the same directory as `main.py`. You can also use the `-c` or `--config` argument to specify a different path.

2.  Run the script:
    ```bash
    python3 main.py
    ```

### Configuration

The `config.ini` file is used to enable plugins and configure their behavior.

Here is an example configuration:

```ini
[main]
# A comma-separated list of plugins to load.
enabled_plugins = battery, volume_pactl, iwd, brightness
# The default timeout for notifications in milliseconds.
# This can be overwritten by individual plugins.
timeout = 1000
# A directory to search for icons if they are not given as a full path.
icon_theme_dir = /usr/share/icons/Cosmic/scalable/
# The directory where icons are cached.
icon_cache_dir = .icon_cache

[battery]
on_message = Power adapter connected
off_message = Power adapter disconnected
low_message = Battery is low
critical_message = Battery is critically low
on_icon = ac-adapter
off_icon = battery-full
low_icon = battery-low
critical_icon = battery-caution

[volume_pactl]
high_icon = audio-volume-high
medium_icon = audio-volume-medium
low_icon = audio-volume-low
muted_icon = audio-volume-muted

[iwd]
connected_icon = network-wireless
disconnected_icon = network-wireless-offline
connected_message = Connected to {ssid}
disconnected_message = Network disconnected

[brightness]
high_icon = display-brightness-high-symbolic
medium_icon = display-brightness-medium-symbolic
low_icon = display-brightness-low-symbolic
```

The `[main]` section has the following options:
*   `enabled_plugins`: A comma-separated list of plugins to load.
*   `timeout`: The default timeout for notifications in milliseconds. This can be overwritten by individual plugins.
*   `icon_theme_dir`: A directory to search for icons if they are not given as a full path.
*   `icon_cache_dir`: The directory where icons are cached.

Each plugin can have its own section (e.g., `[battery]`) for its specific configuration options.

## Creating Plugins

You can easily create your own plugins:

1.  Create a new Python file in the `plugins/` directory (e.g., `my_plugin.py`).
2.  In that file, create a class named `Plugin`.
3.  The `__init__` method of your `Plugin` class will receive a `PluginContext` object.
4.  The `PluginContext` object provides:
    *   `log()`: A logging helper.
    *   `get_config()`: A method to read from the plugin's configuration section.
    *   `notify()`: A method to send desktop notifications.
    *   `close_notification()`: A method to close a previously sent notification.
    *   `get_icon()`: A helper to get an icon from the configured theme or a fallback.
    *   `system_bus`: A D-Bus system bus connection.
    *   `session_bus`: A D-Bus session bus connection.

Here is a simple example from `plugins/dummy.py`:

```python
"""
Dummy Plugin to demonstrate the base structure of a plugin.
"""
from main import PluginContext

class Plugin:
    """
    Dummy Plugin to demonstrate the base structure of a plugin.
    """
    def __init__(self, ctx: PluginContext):
        self.ctx = ctx
        self.ctx.notify("Dummy plugin loaded!")
```

## License

This project is licensed under the GNU General Public License v3.0. See the [COPYING](COPYING) file for the full license text.