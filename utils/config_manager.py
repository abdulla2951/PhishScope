"""
utils/config_manager.py
------------------------
Gestiona la configuración persistente de la aplicación (colores, idioma,
carpeta de exportación, animaciones) guardada en config/settings.json.
"""

import json
import os
from utils.logger import get_logger
from utils.paths import app_base_dir

logger = get_logger(__name__)

BASE_DIR = app_base_dir()
CONFIG_DIR = os.path.join(BASE_DIR, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_CONFIG = {
    "theme": {
        "bg_color": "#0b111e",
        "accent_color": "#38bdf8",
        "text_color": "#f1f5f9",
        "card_color": "#131a29",
        "sidebar_color": "#0d1420"
    },
    "language": "es",
    "export_folder": os.path.join(BASE_DIR, "export", "output"),
    "animations_enabled": True,
    "window_size": "1200x750"
}


class ConfigManager:
    """Carga, expone y persiste la configuración de la aplicación."""

    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._load()

    def _load(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    stored = json.load(f)
                # merge superficial para preservar nuevas claves por defecto
                merged = DEFAULT_CONFIG.copy()
                merged.update(stored)
                if "theme" in stored:
                    merged["theme"] = {**DEFAULT_CONFIG["theme"], **stored["theme"]}
                self._config = merged
            except (json.JSONDecodeError, OSError) as e:
                logger.error(f"No se pudo leer settings.json, usando valores por defecto: {e}")
                self._config = DEFAULT_CONFIG.copy()
        else:
            self.save()

    def save(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except OSError as e:
            logger.error(f"No se pudo guardar settings.json: {e}")

    def get(self, key, default=None):
        return self._config.get(key, default)

    def set(self, key, value):
        self._config[key] = value
        self.save()

    def get_theme(self):
        return self._config.get("theme", DEFAULT_CONFIG["theme"])

    def set_theme_color(self, key, value):
        theme = self._config.setdefault("theme", {})
        theme[key] = value
        self.save()

    @property
    def export_folder(self):
        folder = self._config.get("export_folder", DEFAULT_CONFIG["export_folder"])
        os.makedirs(folder, exist_ok=True)
        return folder


# Instancia única compartida por toda la app
config = ConfigManager()
