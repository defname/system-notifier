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