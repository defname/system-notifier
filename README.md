# D-Bus Notifier

A simple and extensible system event monitor for Linux that uses D-Bus to listen for events and sends desktop notifications.

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
*   **Volume**: A placeholder for a volume change notifier.
*   **Dummy**: A simple boilerplate for creating new plugins.

## Dependencies

The script requires the following:

*   Python 3
*   `python3-dbus`
*   `python3-gi`
*   GObject introspection bindings for `Notify` (`gir1.2-notify-0.7`)

On a Debian-based system, you can install these with:

```bash
sudo apt-get install python3-gi python3-dbus gir1.2-notify-0.7
```

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/dbus-notifier.git
    cd dbus-notifier
    ```
2.  Install the dependencies as described above.

## Usage

1.  Create a configuration file named `config.ini` in the same directory as `main.py`. You can also use the `-c` or `--config` argument to specify a different path.

2.  Run the script:
    ```bash
    ./main.py
    ```

### Configuration

The `config.ini` file is used to enable plugins and configure their behavior.

Here is an example configuration:

```ini
[main]
enabled_plugins = battery, volume

[battery]
on_message = Power adapter connected
off_message = Power adapter disconnected
low_message = Battery is low
critical_message = Battery is critically low
on_icon = ac-adapter
off_icon = battery-full
low_icon = battery-low
critical_icon = battery-caution
```

The `[main]` section has one option:
*   `enabled_plugins`: A comma-separated list of plugins to load.

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

This project is not licensed. Consider adding an open-source license like MIT.
