"""
utils/paths.py
----------------
Resolución del directorio base de la aplicación. En modo fuente es la raíz
del proyecto; en ejecutables PyInstaller es el directorio donde vive el .exe,
para que configuración, logs e historial persistan junto al ejecutable.
"""

import os
import sys


def app_base_dir() -> str:
    """Directorio base persistente de la aplicación."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def app_path(*parts) -> str:
    """Une partes a la raíz persistente de la aplicación."""
    return os.path.join(app_base_dir(), *parts)
