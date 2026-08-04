"""
gui/widgets/result_card.py
------------------------------
Tarjeta moderna reutilizable para mostrar un bloque de resultado del
análisis: icono, título, descripción y estado con color semántico.
"""

import customtkinter as ctk

STATUS_COLORS = {
    "ok": "#00e676",
    "warning": "#ffd600",
    "danger": "#ff9100",
    "critical": "#ff1744",
    "neutral": "#38bdf8",
}


class ResultCard(ctk.CTkFrame):
    """Tarjeta con icono, título, descripción y badge de estado."""

    def __init__(self, master, icon: str, title: str, description: str,
                 status: str = "neutral", card_color: str = "#151515",
                 accent_color: str = "#009dff", **kwargs):
        super().__init__(master, fg_color=card_color, corner_radius=14, **kwargs)

        status_color = STATUS_COLORS.get(status, accent_color)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 4))

        icon_label = ctk.CTkLabel(
            header, text=icon, font=("Segoe UI Emoji", 20), text_color=accent_color
        )
        icon_label.pack(side="left")

        title_label = ctk.CTkLabel(
            header, text=title, font=("Segoe UI", 15, "bold"), text_color="#ffffff"
        )
        title_label.pack(side="left", padx=(8, 0))

        badge = ctk.CTkLabel(
            header, text="", width=14, height=14, corner_radius=7, fg_color=status_color
        )
        badge.pack(side="right")

        desc_label = ctk.CTkLabel(
            self, text=description, font=("Segoe UI", 12), text_color="#b0b0b0",
            justify="left", anchor="w", wraplength=340
        )
        desc_label.pack(fill="x", padx=16, pady=(0, 14))

    @staticmethod
    def status_from_bool(is_good: bool, warn_only: bool = False) -> str:
        if is_good:
            return "ok"
        return "warning" if warn_only else "critical"
