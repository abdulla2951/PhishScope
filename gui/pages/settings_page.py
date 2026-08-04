"""
gui/pages/settings_page.py
------------------------------
Permite cambiar colores del tema, idioma, carpeta de exportación y
activar/desactivar animaciones. Los cambios se persisten en
config/settings.json mediante ConfigManager.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from utils.config_manager import config


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, theme, on_theme_change=None, on_animations_change=None, **kwargs):
        super().__init__(master, fg_color=theme["bg_color"], **kwargs)
        self.theme = theme
        self.on_theme_change = on_theme_change
        self.on_animations_change = on_animations_change
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Configuración", font=("Segoe UI", 24, "bold"),
                     text_color="#ffffff").pack(anchor="w", padx=32, pady=(28, 20))

        # --- Colores del tema ---
        color_card = self._section_card("Colores del tema")
        self.color_entries = {}
        for key, label in [
            ("bg_color", "Color de fondo"),
            ("accent_color", "Color de acento"),
            ("card_color", "Color de tarjetas"),
        ]:
            row = ctk.CTkFrame(color_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=6)
            ctk.CTkLabel(row, text=label, font=("Segoe UI", 12), text_color="#c0c0c0",
                         width=160, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(row, width=140, height=30)
            entry.insert(0, config.get_theme().get(key, ""))
            entry.pack(side="left", padx=8)
            self.color_entries[key] = entry

        ctk.CTkButton(
            color_card, text="Aplicar colores", height=36, corner_radius=8,
            fg_color=self.theme["accent_color"], hover_color="#0077cc",
            command=self._apply_colors
        ).pack(anchor="w", padx=20, pady=(6, 16))

        # --- Idioma ---
        lang_card = self._section_card("Idioma")
        self.lang_var = ctk.StringVar(value=config.get("language", "es"))
        lang_row = ctk.CTkFrame(lang_card, fg_color="transparent")
        lang_row.pack(fill="x", padx=20, pady=(6, 16))
        ctk.CTkOptionMenu(
            lang_row, values=["es", "en"], variable=self.lang_var,
            fg_color=self.theme["card_color"], button_color=self.theme["accent_color"],
            command=self._change_language
        ).pack(side="left")
        ctk.CTkLabel(lang_row, text="(reinicia la app para aplicar el idioma por completo)",
                     font=("Segoe UI", 10), text_color="#707070").pack(side="left", padx=10)

        # --- Carpeta de exportación ---
        export_card = self._section_card("Carpeta de exportación")
        self.export_path_label = ctk.CTkLabel(
            export_card, text=config.export_folder, font=("Segoe UI", 11), text_color="#a0a0a0"
        )
        self.export_path_label.pack(anchor="w", padx=20, pady=(6, 8))
        ctk.CTkButton(
            export_card, text="Cambiar carpeta", height=36, corner_radius=8,
            fg_color=self.theme["accent_color"], hover_color="#0077cc",
            command=self._change_export_folder
        ).pack(anchor="w", padx=20, pady=(0, 16))

        # --- Animaciones ---
        anim_card = self._section_card("Animaciones")
        self.anim_switch_var = ctk.BooleanVar(value=config.get("animations_enabled", True))
        ctk.CTkSwitch(
            anim_card, text="Activar animaciones suaves", variable=self.anim_switch_var,
            progress_color=self.theme["accent_color"], command=self._toggle_animations
        ).pack(anchor="w", padx=20, pady=(6, 16))

    def _section_card(self, title):
        card = ctk.CTkFrame(self, fg_color=self.theme["card_color"], corner_radius=14)
        card.pack(fill="x", padx=32, pady=8)
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w", padx=20, pady=(14, 4))
        return card

    def _apply_colors(self):
        for key, entry in self.color_entries.items():
            value = entry.get().strip()
            if value:
                config.set_theme_color(key, value)
        messagebox.showinfo(
            "PhishScope",
            "Colores guardados. Reinicia la aplicación para aplicarlos completamente."
        )
        if self.on_theme_change:
            self.on_theme_change(config.get_theme())

    def _change_language(self, value):
        config.set("language", value)

    def _change_export_folder(self):
        folder = filedialog.askdirectory(title="Selecciona la carpeta de exportación")
        if folder:
            config.set("export_folder", folder)
            self.export_path_label.configure(text=folder)

    def _toggle_animations(self):
        enabled = self.anim_switch_var.get()
        config.set("animations_enabled", enabled)
        if self.on_animations_change:
            self.on_animations_change(enabled)
