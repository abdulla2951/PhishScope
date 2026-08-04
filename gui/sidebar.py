"""
gui/sidebar.py
-----------------
Barra lateral de navegación de PhishScope: logo, identidad de marca y
navegación limpia con resaltado del ítem activo.
"""

import os

import customtkinter as ctk
from PIL import Image

from utils.resources import resource_path
from utils.constants import APP_NAME, APP_TAGLINE, APP_VERSION

MENU_ITEMS = [
    ("home", "Inicio"),
    ("analyzer", "Analizador de URLs"),
    ("history", "Historial"),
    ("exports", "Exportaciones"),
    ("settings", "Configuración"),
    ("about", "Acerca de"),
]


class Sidebar(ctk.CTkFrame):
    """Barra lateral con botones de navegación entre páginas."""

    def __init__(self, master, on_navigate, sidebar_color="#0d1420",
                 accent_color="#38bdf8", **kwargs):
        super().__init__(master, fg_color=sidebar_color, width=232, corner_radius=0, **kwargs)
        self.on_navigate = on_navigate
        self.accent_color = accent_color
        self.buttons = {}
        self.active_key = None

        self.pack_propagate(False)
        self.grid_rowconfigure(2, weight=1)

        # --- Logo e identidad ---
        logo_path = resource_path("logo.png")
        self.logo_image = ctk.CTkImage(
            light_image=Image.open(logo_path),
            dark_image=Image.open(logo_path),
            size=(72, 72),
        ) if os.path.exists(logo_path) else None

        logo_area = ctk.CTkFrame(self, fg_color="transparent")
        logo_area.pack(pady=(24, 0))

        if self.logo_image:
            ctk.CTkLabel(logo_area, image=self.logo_image, text="").pack()

        brand = ctk.CTkLabel(
            logo_area, text=APP_NAME, font=("Segoe UI", 22, "bold"),
            text_color="#ffffff"
        )
        brand.pack(pady=(8, 0))

        tagline = ctk.CTkLabel(
            logo_area, text=APP_TAGLINE, font=("Segoe UI", 10),
            text_color="#5b6b82"
        )
        tagline.pack(pady=(0, 4))

        divider = ctk.CTkFrame(self, height=1, fg_color="#1d2939", corner_radius=0)
        divider.pack(fill="x", padx=18, pady=(18, 12))

        # --- Navegación ---
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=12)

        for key, label in MENU_ITEMS:
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                anchor="w",
                fg_color="transparent",
                hover_color="#172136",
                text_color="#a9b4c4",
                font=("Segoe UI", 13),
                corner_radius=8,
                height=38,
                command=lambda k=key: self._handle_click(k),
            )
            btn.pack(fill="x", pady=3)
            self.buttons[key] = btn

        self.set_active("home")

        # --- Pie con versión ---
        version_label = ctk.CTkLabel(
            self, text=f"v{APP_VERSION}", font=("Segoe UI", 10),
            text_color="#445067"
        )
        version_label.pack(side="bottom", pady=(0, 16))

    def _handle_click(self, key):
        self.set_active(key)
        self.on_navigate(key)

    def set_active(self, key):
        self.active_key = key
        for k, btn in self.buttons.items():
            if k == key:
                btn.configure(fg_color=self.accent_color, text_color="#0b111e",
                              font=("Segoe UI", 13, "bold"))
            else:
                btn.configure(fg_color="transparent", text_color="#a9b4c4",
                              font=("Segoe UI", 13))
