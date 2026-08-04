"""
utils/logger.py
----------------
Sistema de logging centralizado para PhishScope.
Registra automáticamente errores y eventos relevantes en logs/app.log
con rotación de archivos para evitar crecimiento indefinido.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from utils.paths import app_base_dir

LOG_DIR = os.path.join(app_base_dir(), "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")


def get_logger(name: str = "PhishScope") -> logging.Logger:
    """
    Devuelve un logger configurado con salida a archivo (rotativo) y consola.

    Args:
        name: nombre del logger (normalmente __name__ del módulo que lo solicita).

    Returns:
        Instancia de logging.Logger lista para usar.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        # Ya configurado (evita handlers duplicados si se llama varias veces)
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler de archivo con rotación (5 MB x 3 backups)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler de consola (solo advertencias y errores para no ensuciar la GUI)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
