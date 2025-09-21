""" Provied the get_icon helper function. """
from utils.helper import log
import os
import cairosvg
from lxml import etree


def get_icon(icon_name: str, theme_dir: str, cache_dir: str):
    """ Find the icon file and convert it to PNG if necessary.

    If icon_name is not a filename the following steps are taken:
    - check cache_dir for icon_name and return the correct file path
    - search theme_dir for icon_name
    - if the icon is found and it is not a SVG file, copy it to cache_dir and return the path
    - if the icon is a SVG file, convert it to PNG and save it to cache_dir and return the path
    """
    # check if icon_name is a filename
    if os.path.isfile(icon_name):
        return os.path.realpath(icon_name)

    # check if the icon is already in the cache dir return it's path
    if os.path.isfile(os.path.join(cache_dir, icon_name+".png")):
        return os.path.realpath(os.path.join(cache_dir, icon_name+".png"))
    
    # find the icon in the icon theme directory
    file_path: str = ""
    try:
        file_path = _find_icon_file(icon_name, theme_dir)
        log("Using icon: " + file_path)
    except FileNotFoundError:
        log("cannot find icon: " + icon_name)
        return ""
    
    # convert if necessary
    if file_path.endswith(".svg"):
        try:
            file_path = _convert_svg_to_png(icon_name, file_path, cache_dir)
        except Exception:
            log("Cannot convert icon file")
            return ""
    else:
        # copy otherwise
        try:
            file_path = _copy_to_cache_dir(file_path, cache_dir)
        except Exception:
            log("Cannot copy icon file")
            return ""

    return os.path.realpath(file_path)

def _copy_to_cache_dir(file_path: str, cache_dir: str):
    cache_dir = _get_cache_dir(cache_dir)
    new_path = os.path.join(cache_dir, os.path.basename(file_path))
    os.copy_file_range(file_path, new_path)
    return new_path


def _convert_svg_to_png(icon_name: str, svg_path: str, cache_dir: str):
    cache_dir = _get_cache_dir(cache_dir)
    png_path = os.path.join(cache_dir, icon_name + ".png")
    cairosvg.svg2png(url=svg_path, write_to=png_path, dpi=96, output_width=256)
    return png_path

def _find_icon_file(icon_name: str, theme_dir: str):
    for root, dirs, files in os.walk(theme_dir):
        for file in files:
            if file.startswith(icon_name):
                return os.path.join(root, file)
    raise FileNotFoundError

def _get_cache_dir(cache_dir: str):
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    return cache_dir
