"""
gui/pages/about_page.py
---------------------------
Información sobre PhishScope, su propósito y las tecnologías utilizadas.
"""

import customtkinter as ctk

from utils.constants import APP_NAME, APP_VERSION, APP_DESCRIPTION


class AboutPage(ctk.CTkFrame):
    def __init__(self, master, theme, **kwargs):
        super().__init__(master, fg_color=theme["bg_color"], **kwargs)
        self.theme = theme
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Acerca de", font=("Segoe UI", 24, "bold"),
                     text_color="#ffffff").pack(anchor="w", padx=32, pady=(28, 20))

        card = ctk.CTkFrame(self, fg_color=self.theme["card_color"], corner_radius=12)
        card.pack(fill="x", padx=32, pady=8)

        ctk.CTkLabel(card, text=APP_NAME, font=("Segoe UI", 20, "bold"),
                     text_color=self.theme["accent_color"]).pack(anchor="w", padx=24, pady=(20, 4))
        ctk.CTkLabel(card, text=f"Versión {APP_VERSION}", font=("Segoe UI", 12),
                     text_color="#8b9ab0").pack(anchor="w", padx=24)

        description = (
            f"{APP_DESCRIPTION}\n\n"
            "Esta aplicación analiza únicamente URLs proporcionadas por el usuario y no "
            "incluye funciones ofensivas ni automatiza ataques contra terceros.\n\n"
            f"{APP_NAME} es una herramienta de análisis defensivo de URLs, pensada como "
            "el primer módulo de una futura suite de ciberseguridad que incorpore nuevas "
            "utilidades defensivas (escáner de puertos, analizador de hashes, utilidades "
            "DNS/WHOIS, y más) bajo una misma identidad visual."
        )
        ctk.CTkLabel(card, text=description, font=("Segoe UI", 12.5), text_color="#b6c2d4",
                     justify="left", wraplength=680, anchor="w").pack(
            anchor="w", padx=24, pady=(16, 24))

        tech_card = ctk.CTkFrame(self, fg_color=self.theme["card_color"], corner_radius=12)
        tech_card.pack(fill="x", padx=32, pady=8)
        ctk.CTkLabel(tech_card, text="Tecnologías utilizadas", font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w", padx=24, pady=(18, 6))
        techs = "Python 3.13 · CustomTkinter · ttkbootstrap · requests · cryptography · " \
                "python-whois · dnspython · tldextract · validators · Pillow · SQLite · reportlab"
        ctk.CTkLabel(tech_card, text=techs, font=("Segoe UI", 12), text_color="#93a1b5",
                     wraplength=680, justify="left", anchor="w").pack(
            anchor="w", padx=24, pady=(0, 20))
