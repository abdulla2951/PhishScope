"""
gui/pages/home_page.py
-------------------------
Página de bienvenida de PhishScope: resumen del proyecto y estadísticas
rápidas del historial (total de análisis, promedio de riesgo, último).
"""

import customtkinter as ctk
from database.db_manager import db
from utils.constants import APP_NAME


class HomePage(ctk.CTkFrame):
    def __init__(self, master, theme, **kwargs):
        super().__init__(master, fg_color=theme["bg_color"], **kwargs)
        self.theme = theme
        self._build()

    def _build(self):
        title = ctk.CTkLabel(
            self, text=f"Bienvenido a {APP_NAME}",
            font=("Segoe UI", 26, "bold"), text_color="#ffffff"
        )
        title.pack(anchor="w", padx=32, pady=(32, 4))

        subtitle = ctk.CTkLabel(
            self,
            text="Analiza URLs en busca de indicadores de phishing, SSL débil,\n"
                 "dominios sospechosos y configuraciones inseguras.",
            font=("Segoe UI", 13), text_color="#8b9ab0", justify="left"
        )
        subtitle.pack(anchor="w", padx=32, pady=(0, 24))

        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=32)

        records = db.get_all(limit=1000)
        total = len(records)
        avg_score = round(sum(r["puntaje"] or 0 for r in records) / total, 1) if total else 0
        last_url = records[0]["url"] if records else "—"

        self._stat_card(stats_frame, "Análisis realizados", str(total))
        self._stat_card(stats_frame, "Puntaje promedio", str(avg_score))
        self._stat_card(stats_frame, "Último análisis", last_url, wide=True)

    def _stat_card(self, parent, label, value, wide=False):
        card = ctk.CTkFrame(parent, fg_color=self.theme["card_color"], corner_radius=12)
        card.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        value_label = ctk.CTkLabel(
            card, text=value, font=("Segoe UI", 20, "bold"), text_color="#ffffff",
            wraplength=260 if wide else 160, justify="left"
        )
        value_label.pack(anchor="w", padx=16, pady=(16, 2))

        ctk.CTkLabel(card, text=label, font=("Segoe UI", 11),
                     text_color="#8b9ab0").pack(anchor="w", padx=16, pady=(0, 16))

    def refresh(self):
        """Reconstruye el contenido para reflejar cambios recientes en el historial."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build()
