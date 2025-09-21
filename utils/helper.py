"""Helper functions"""
from globals import LOG_FILE, LOG_TAG_WIDTH

def log(*args, tag="main", **kwargs):
    """Helper for log messages"""
    print(f"{"[" + tag + "]":{LOG_TAG_WIDTH}}", *args, file=LOG_FILE, **kwargs)
