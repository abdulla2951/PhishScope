"""
gui/pages/history_page.py
-----------------------------
Muestra el historial de análisis guardados en SQLite, con búsqueda y
opción de borrado individual o total.
"""

import customtkinter as ctk
from tkinter import messagebox
from database.db_manager import db

LEVEL_COLORS = {
    "Seguro": "#00e676",
    "Medio": "#ffd600",
    "Alto": "#ff9100",
    "Crítico": "#ff1744",
}


class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, theme, **kwargs):
        super().__init__(master, fg_color=theme["bg_color"], **kwargs)
        self.theme = theme
        self._build()

    def _build(self):
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=32, pady=(28, 12))

        ctk.CTkLabel(header_row, text="Historial", font=("Segoe UI", 24, "bold"),
                     text_color="#ffffff").pack(side="left")

        clear_btn = ctk.CTkButton(
            header_row, text="Borrar todo", width=120, height=32, corner_radius=8,
            fg_color="#2a0000", hover_color="#ff1744", text_color="#ff8080",
            font=("Segoe UI", 12), command=self._clear_all
        )
        clear_btn.pack(side="right")

        search_row = ctk.CTkFrame(self, fg_color="transparent")
        search_row.pack(fill="x", padx=32, pady=(0, 12))

        self.search_entry = ctk.CTkEntry(
            search_row, placeholder_text="Buscar por URL, IP o país...",
            height=38, fg_color=self.theme["card_color"], corner_radius=8
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<Return>", lambda e: self._do_search())

        ctk.CTkButton(
            search_row, text="Buscar", width=90, height=38, corner_radius=8,
            fg_color=self.theme["accent_color"], hover_color="#0077cc",
            command=self._do_search
        ).pack(side="left")

        self.list_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self._load_records(db.get_all())

    def _do_search(self):
        keyword = self.search_entry.get().strip()
        records = db.search(keyword) if keyword else db.get_all()
        self._load_records(records)

    def _load_records(self, records):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        if not records:
            ctk.CTkLabel(self.list_container, text="No hay registros en el historial.",
                         font=("Segoe UI", 13), text_color="#606060").pack(pady=40)
            return

        for rec in records:
            self._build_row(rec)

    def _build_row(self, rec):
        row = ctk.CTkFrame(self.list_container, fg_color=self.theme["card_color"], corner_radius=12)
        row.pack(fill="x", pady=5)

        color = LEVEL_COLORS.get(rec["nivel"], self.theme["accent_color"])

        badge = ctk.CTkLabel(row, text="", width=10, height=10, corner_radius=5, fg_color=color)
        badge.pack(side="left", padx=(14, 10), pady=12)

        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=10)

        ctk.CTkLabel(info_frame, text=rec["url"], font=("Segoe UI", 13, "bold"),
                     text_color="#ffffff", anchor="w").pack(fill="x")

        meta = f"{rec['fecha']} {rec['hora']}  •  IP: {rec['ip'] or '—'}  •  País: {rec['pais'] or '—'}  •  HTTP {rec['estado_http'] or '—'}"
        ctk.CTkLabel(info_frame, text=meta, font=("Segoe UI", 11), text_color="#909090",
                     anchor="w").pack(fill="x")

        score_label = ctk.CTkLabel(
            row, text=f"{rec['puntaje']}\n{rec['nivel']}", font=("Segoe UI", 12, "bold"),
            text_color=color, justify="center"
        )
        score_label.pack(side="left", padx=16)

        del_btn = ctk.CTkButton(
            row, text="🗑", width=36, height=32, corner_radius=8,
            fg_color="transparent", hover_color="#2a0000", text_color="#ff8080",
            command=lambda rid=rec["id"]: self._delete_record(rid)
        )
        del_btn.pack(side="right", padx=14)

    def _delete_record(self, record_id):
        db.delete_record(record_id)
        self._do_search()

    def _clear_all(self):
        confirm = messagebox.askyesno(
            "PhishScope", "¿Seguro que deseas borrar todo el historial? Esta acción no se puede deshacer."
        )
        if confirm:
            db.clear_all()
            self._load_records([])

    def refresh(self):
        self._do_search() if self.search_entry.get().strip() else self._load_records(db.get_all())
