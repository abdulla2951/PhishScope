"""
utils/resources.py
--------------------
Resolución de rutas a recursos empaquetados (assets/...). Funciona tanto en
modo fuente como dentro de un ejecutable PyInstaller (sys._MEIPASS).
"""

import os
import sys

from utils.paths import app_base_dir


def _bundle_dir() -> str:
    """Directorio donde PyInstaller extrae los recursos empaquetados."""
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", app_base_dir())
    return app_base_dir()


def resource_path(relative: str) -> str:
    """Devuelve la ruta absoluta de un recurso dentro de la carpeta assets/."""
    return os.path.join(_bundle_dir(), "assets", relative)


def resource_exists(relative: str) -> bool:
    return os.path.exists(resource_path(relative))
