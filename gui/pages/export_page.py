"""
gui/pages/export_page.py
----------------------------
Permite exportar el historial completo (o el resultado filtrado) a
PDF, JSON, CSV o HTML, y muestra la carpeta de exportación actual.
"""

import customtkinter as ctk
from tkinter import messagebox
import os
import subprocess
import sys

from database.db_manager import db
from export import exporter
from utils.config_manager import config


class ExportPage(ctk.CTkFrame):
    def __init__(self, master, theme, **kwargs):
        super().__init__(master, fg_color=theme["bg_color"], **kwargs)
        self.theme = theme
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="Exportaciones", font=("Segoe UI", 24, "bold"),
                     text_color="#ffffff").pack(anchor="w", padx=32, pady=(28, 8))

        ctk.CTkLabel(
            self, text="Exporta el historial completo de análisis en el formato que prefieras.",
            font=("Segoe UI", 13), text_color="#909090"
        ).pack(anchor="w", padx=32, pady=(0, 20))

        card = ctk.CTkFrame(self, fg_color=self.theme["card_color"], corner_radius=14)
        card.pack(fill="x", padx=32, pady=8)

        ctk.CTkLabel(card, text="Carpeta de exportación:", font=("Segoe UI", 12, "bold"),
                     text_color="#ffffff").pack(anchor="w", padx=20, pady=(18, 2))
        self.folder_label = ctk.CTkLabel(card, text=config.export_folder, font=("Segoe UI", 11),
                                          text_color="#a0a0a0")
        self.folder_label.pack(anchor="w", padx=20, pady=(0, 16))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=32, pady=20)

        formats = [
            ("Exportar historial (PDF)", "pdf"),
            ("Exportar historial (JSON)", "json"),
            ("Exportar historial (CSV)", "csv"),
            ("Exportar historial (HTML)", "html"),
        ]

        for label, fmt in formats:
            btn = ctk.CTkButton(
                self, text=label, height=46, corner_radius=10,
                fg_color=self.theme["card_color"], hover_color=self.theme["accent_color"],
                font=("Segoe UI", 13), anchor="w",
                command=lambda f=fmt: self._export_history(f)
            )
            btn.pack(fill="x", padx=32, pady=6)

        open_folder_btn = ctk.CTkButton(
            self, text="Abrir carpeta de exportaciones", height=40, corner_radius=10,
            fg_color=self.theme["accent_color"], hover_color="#0077cc",
            font=("Segoe UI", 12, "bold"), command=self._open_folder
        )
        open_folder_btn.pack(fill="x", padx=32, pady=(16, 8))

    def _export_history(self, fmt):
        records = db.get_all(limit=5000)
        if not records:
            messagebox.showinfo("PhishScope", "El historial está vacío, no hay nada que exportar.")
            return

        try:
            if fmt == "json":
                path = exporter.export_json(records)
            elif fmt == "csv":
                rows = [{k: v for k, v in r.items() if k != "detalle_json"} for r in records]
                path = exporter.export_csv(rows)
            elif fmt == "html":
                path = exporter.export_html({"historial": records})
            else:
                path = exporter.export_pdf({"historial": records})
            messagebox.showinfo("PhishScope", f"Historial exportado correctamente:\n{path}")
        except Exception as e:
            messagebox.showerror("PhishScope", f"No se pudo exportar el historial: {e}")

    def _open_folder(self):
        folder = config.export_folder
        try:
            if sys.platform == "win32":
                os.startfile(folder)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder])
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("PhishScope", f"No se pudo abrir la carpeta: {e}")

    def refresh(self):
        self.folder_label.configure(text=config.export_folder)
