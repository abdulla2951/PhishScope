"""
gui/app.py
------------
Ventana principal de PhishScope. Ensambla el sidebar y las
distintas páginas, gestionando la navegación entre ellas.
"""

import os

import customtkinter as ctk

from gui.sidebar import Sidebar
from gui.pages.home_page import HomePage
from gui.pages.analyzer_page import AnalyzerPage
from gui.pages.history_page import HistoryPage
from gui.pages.export_page import ExportPage
from gui.pages.settings_page import SettingsPage
from gui.pages.about_page import AboutPage
from utils.config_manager import config
from utils.logger import get_logger
from utils.resources import resource_path

logger = get_logger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PhishScopeApp(ctk.CTk):
    """Ventana raíz de la aplicación."""

    def __init__(self):
        super().__init__()

        self.theme = config.get_theme()
        self.animations_enabled = config.get("animations_enabled", True)

        self.title("PhishScope — Analizador de URLs")
        self.geometry(config.get("window_size", "1200x750"))
        self.minsize(980, 640)
        self.configure(fg_color=self.theme["bg_color"])

        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        # Sin esto, cualquier excepción producida dentro de un callback de la GUI
        # (botones, after(), etc.) desaparece en silencio y la pantalla se queda
        # "congelada" sin ningún resultado visible. Al registrarla en el logger,
        # queda constancia en logs/app.log para poder diagnosticarla.
        self.report_callback_exception = self._handle_tk_exception

        self._build_layout()

    def _handle_tk_exception(self, exc_type, exc_value, exc_tb):
        import traceback
        logger.error(
            "Excepción no controlada en la interfaz gráfica:\n"
            + "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        )

    def _build_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(
            self, on_navigate=self.navigate,
            sidebar_color=self.theme["sidebar_color"],
            accent_color=self.theme["accent_color"],
        )
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content_area = ctk.CTkFrame(self, fg_color=self.theme["bg_color"], corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Instanciar todas las páginas (se muestran/ocultan, no se recrean)
        self.pages = {
            "home": HomePage(self.content_area, self.theme),
            "analyzer": AnalyzerPage(
                self.content_area, self.theme,
                on_analysis_complete=self._on_analysis_complete
            ),
            "history": HistoryPage(self.content_area, self.theme),
            "exports": ExportPage(self.content_area, self.theme),
            "settings": SettingsPage(
                self.content_area, self.theme,
                on_theme_change=self._on_theme_change,
                on_animations_change=self._on_animations_change,
            ),
            "about": AboutPage(self.content_area, self.theme),
        }

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.pages["analyzer"].set_animations_enabled(self.animations_enabled)

        self.current_page_key = "home"
        self.pages["home"].tkraise()

    def navigate(self, key: str):
        if key not in self.pages:
            logger.warning(f"Intento de navegar a página desconocida: {key}")
            return

        page = self.pages[key]
        if hasattr(page, "refresh"):
            try:
                page.refresh()
            except Exception as e:
                logger.error(f"Error refrescando página {key}: {e}")

        page.tkraise()
        self.current_page_key = key

    def _on_analysis_complete(self):
        # Refresca estadísticas de inicio y el historial si el usuario vuelve a esas páginas
        if hasattr(self.pages["home"], "refresh"):
            self.pages["home"].refresh()

    def _on_theme_change(self, new_theme):
        # Los colores de tarjetas/acento ya activos requieren reinicio completo
        # para propagarse a todos los widgets; se informa al usuario en Settings.
        self.theme = new_theme

    def _on_animations_change(self, enabled: bool):
        self.animations_enabled = enabled
        self.pages["analyzer"].set_animations_enabled(enabled)


def run_app():
    app = PhishScopeApp()
    app.mainloop()
