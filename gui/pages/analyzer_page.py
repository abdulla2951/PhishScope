"""
gui/pages/analyzer_page.py
------------------------------
Página principal: el usuario pega una URL, presiona "Analizar" y la
aplicación ejecuta todos los análisis en segundo plano, mostrando el
progreso, el medidor de riesgo y tarjetas de resultado modernas.
"""

import threading
from datetime import datetime

import customtkinter as ctk
from tkinter import messagebox

from core.url_analyzer import analyze
from gui.widgets.risk_gauge import RiskGauge
from gui.widgets.result_card import ResultCard
from database.db_manager import db
from export import exporter
from utils.logger import get_logger

logger = get_logger(__name__)


class AnalyzerPage(ctk.CTkFrame):
    def __init__(self, master, theme, on_analysis_complete=None, **kwargs):
        super().__init__(master, fg_color=theme["bg_color"], **kwargs)
        self.theme = theme
        self.on_analysis_complete = on_analysis_complete
        self.current_result = None
        self.animations_enabled = True

        self._build_static_layout()

    # ------------------------------------------------------------------ #
    # Layout
    # ------------------------------------------------------------------ #
    def _build_static_layout(self):
        header = ctk.CTkLabel(
            self, text="Analizador de URLs", font=("Segoe UI", 24, "bold"), text_color="#ffffff"
        )
        header.pack(anchor="w", padx=32, pady=(28, 8))

        input_row = ctk.CTkFrame(self, fg_color="transparent")
        input_row.pack(fill="x", padx=32)

        self.url_entry = ctk.CTkEntry(
            input_row, placeholder_text="Pega una URL aquí (ej: https://ejemplo.com)",
            height=42, font=("Segoe UI", 13),
            fg_color=self.theme["card_color"], border_color=self.theme["accent_color"],
            corner_radius=10
        )
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.url_entry.bind("<Return>", lambda e: self._start_analysis())

        self.analyze_btn = ctk.CTkButton(
            input_row, text="Analizar", width=120, height=42,
            fg_color=self.theme["accent_color"], hover_color="#0077cc",
            corner_radius=10, font=("Segoe UI", 13, "bold"),
            command=self._start_analysis
        )
        self.analyze_btn.pack(side="left")

        self.status_label = ctk.CTkLabel(
            self, text="", font=("Segoe UI", 12), text_color=self.theme["accent_color"]
        )
        self.status_label.pack(anchor="w", padx=32, pady=(8, 0))

        self.progress_bar = ctk.CTkProgressBar(
            self, height=6, fg_color="#1c1c1c", progress_color=self.theme["accent_color"]
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=32, pady=(6, 12))
        self.progress_bar.pack_forget()  # oculto hasta que empiece el análisis

        # Contenedor scrollable para el gauge + tarjetas de resultado
        self.results_container = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self.results_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._show_placeholder()

    def _show_placeholder(self):
        placeholder = ctk.CTkLabel(
            self.results_container,
            text="Ingresa una URL y presiona \"Analizar\" para comenzar.",
            font=("Segoe UI", 13), text_color="#606060"
        )
        placeholder.pack(pady=60)

    def set_animations_enabled(self, enabled: bool):
        self.animations_enabled = enabled

    # ------------------------------------------------------------------ #
    # Ejecución del análisis (en hilo aparte para no bloquear la GUI)
    # ------------------------------------------------------------------ #
    def _start_analysis(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("PhishScope", "Por favor ingresa una URL.")
            return

        self.analyze_btn.configure(state="disabled", text="Analizando...")
        self.progress_bar.pack(fill="x", padx=32, pady=(6, 12))
        self.progress_bar.set(0)
        self.status_label.configure(text="Iniciando análisis...")

        for widget in self.results_container.winfo_children():
            widget.destroy()

        thread = threading.Thread(target=self._run_analysis_thread, args=(url,), daemon=True)
        thread.start()

    def _run_analysis_thread(self, url):
        steps_done = {"count": 0}
        total_steps = 8

        def progress_callback(step_text):
            steps_done["count"] += 1
            fraction = min(steps_done["count"] / total_steps, 1.0)
            self.after(0, lambda: self._update_progress(step_text, fraction))

        try:
            result = analyze(url, progress_callback=progress_callback)
        except Exception as e:
            logger.error(f"Error inesperado analizando {url}: {e}")
            self.after(0, lambda: self._on_analysis_error(str(e)))
            return

        self.after(0, lambda: self._on_analysis_done(result))

    def _update_progress(self, step_text, fraction):
        self.status_label.configure(text=step_text)
        self.progress_bar.set(fraction)

    def _on_analysis_error(self, error_msg):
        self.analyze_btn.configure(state="normal", text="Analizar")
        self.status_label.configure(text="Ocurrió un error durante el análisis.")
        messagebox.showerror("PhishScope", f"Error durante el análisis:\n{error_msg}")

    # ------------------------------------------------------------------ #
    # Renderizado de resultados
    # ------------------------------------------------------------------ #
    def _on_analysis_done(self, result):
        self.analyze_btn.configure(state="normal", text="Analizar")
        self.progress_bar.pack_forget()

        if not result.valid_input:
            self.status_label.configure(text=result.input_error)
            messagebox.showwarning("PhishScope", result.input_error)
            return

        self.current_result = result

        try:
            self._render_results(result)
        except Exception as e:
            logger.error(f"Error renderizando resultados para {result.normalized_url}: {e}", exc_info=True)
            self.status_label.configure(text="El análisis terminó, pero ocurrió un error mostrando los resultados.")
            messagebox.showerror(
                "PhishScope",
                f"El análisis se completó pero no se pudo mostrar en pantalla:\n{e}\n\n"
                "Revisa logs\\app.log para más detalle."
            )
            return

        self.status_label.configure(text=f"Análisis completado para {result.domain}")

        try:
            self._save_to_history(result)
        except Exception as e:
            logger.error(f"Error guardando historial para {result.normalized_url}: {e}", exc_info=True)

        if self.on_analysis_complete:
            self.on_analysis_complete()

    def _render_results(self, result):
        for widget in self.results_container.winfo_children():
            widget.destroy()

        top_row = ctk.CTkFrame(self.results_container, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 16))

        gauge = RiskGauge(top_row, size=200, bg_color=self.theme["bg_color"])
        gauge.set_animations_enabled(self.animations_enabled)
        gauge.pack(side="left", padx=(0, 24))
        gauge.set_score(result.risk.score, result.risk.level, result.risk.color)

        summary = ctk.CTkFrame(top_row, fg_color=self.theme["card_color"], corner_radius=14)
        summary.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(summary, text=result.normalized_url, font=("Segoe UI", 15, "bold"),
                     text_color="#ffffff", wraplength=500, justify="left").pack(
            anchor="w", padx=18, pady=(16, 4))
        ctk.CTkLabel(summary, text=f"Dominio: {result.domain}", font=("Segoe UI", 12),
                     text_color="#a0a0a0").pack(anchor="w", padx=18)

        factors_triggered = [f.label for f in result.risk.factors if f.triggered]
        factors_text = "\n".join(f"• {f}" for f in factors_triggered) or "No se detectaron factores de riesgo relevantes."
        ctk.CTkLabel(summary, text=factors_text, font=("Segoe UI", 12),
                     text_color="#c0c0c0", justify="left", anchor="w",
                     wraplength=500).pack(anchor="w", padx=18, pady=(8, 16))

        # Grid de tarjetas de resultado
        grid = ctk.CTkFrame(self.results_container, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        grid.grid_columnconfigure((0, 1), weight=1)

        cards = self._build_cards(result, parent=grid)
        for i, card in enumerate(cards):
            row, col = divmod(i, 2)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

        export_row = ctk.CTkFrame(self.results_container, fg_color="transparent")
        export_row.pack(fill="x", pady=(16, 4))
        ctk.CTkLabel(export_row, text="Exportar este análisis:", font=("Segoe UI", 12),
                     text_color="#909090").pack(side="left", padx=(4, 12))
        for label, fmt in [("PDF", "pdf"), ("JSON", "json"), ("CSV", "csv"), ("HTML", "html")]:
            ctk.CTkButton(
                export_row, text=label, width=70, height=30, corner_radius=8,
                fg_color="#1c1c1c", hover_color=self.theme["accent_color"],
                font=("Segoe UI", 11), command=lambda f=fmt: self._export_current(f)
            ).pack(side="left", padx=4)

    def _build_cards(self, result, parent):
        cards = []
        accent = self.theme["accent_color"]
        card_color = self.theme["card_color"]

        # SSL
        ssl = result.ssl
        ssl_desc = ssl.error or f"Emisor: {ssl.issuer or '—'}\nExpira en {ssl.days_until_expiry} días\nTLS: {ssl.tls_version or '—'}"
        cards.append(ResultCard(
            parent, "🔒", "Certificado SSL", ssl_desc,
            status=ResultCard.status_from_bool(ssl.valid), card_color=card_color, accent_color=accent
        ))

        # WHOIS / dominio
        di = result.domain_info
        age_txt = f"{di.domain_age_days} días" if di.domain_age_days is not None else "Desconocida"
        di_desc = di.error or f"Registrador: {di.registrar or '—'}\nCreado: {di.creation_date or '—'}\nEdad: {age_txt}"
        is_new = di.domain_age_days is not None and di.domain_age_days < 180
        cards.append(ResultCard(
            parent, "📅", "Información del dominio", di_desc,
            status=ResultCard.status_from_bool(not is_new, warn_only=True),
            card_color=card_color, accent_color=accent
        ))

        # Estructura de URL
        uh = result.url_heuristics
        flags_txt = "\n".join(f"• {f}" for f in uh.suspicious_flags) or "Sin patrones sospechosos detectados."
        cards.append(ResultCard(
            parent, "🧬", "Estructura de la URL", flags_txt,
            status=ResultCard.status_from_bool(len(uh.suspicious_flags) == 0),
            card_color=card_color, accent_color=accent
        ))

        # Redirecciones
        rd = result.redirects
        rd_desc = rd.error or f"Saltos: {rd.redirect_count}\nDestino final: {rd.final_url}"
        cards.append(ResultCard(
            parent, "↪", "Redirecciones", rd_desc,
            status=ResultCard.status_from_bool(rd.redirect_count < 3, warn_only=True),
            card_color=card_color, accent_color=accent
        ))

        # DNS
        dns_res = result.dns
        dns_lines = []
        for rtype, values in dns_res.records.items():
            if values:
                dns_lines.append(f"{rtype}: {', '.join(values[:3])}")

        if dns_lines:
            dns_desc = "\n".join(dns_lines)
            dns_status = "neutral"
        elif dns_res.errors:
            # Hubo fallos reales en la consulta (timeout, NXDOMAIN, servidor
            # DNS inalcanzable, etc.) — no es lo mismo que "no hay registros".
            error_lines = [f"{rtype}: {msg}" for rtype, msg in dns_res.errors.items()]
            dns_desc = "No se pudieron obtener los registros DNS:\n" + "\n".join(error_lines)
            dns_status = "warning"
        else:
            dns_desc = "Sin registros DNS destacables."
            dns_status = "neutral"

        cards.append(ResultCard(
            parent, "🌐", "Registros DNS", dns_desc,
            status=dns_status, card_color=card_color, accent_color=accent
        ))

        # Geolocalización
        geo = result.geo
        ip_line = f"IP: {geo.ipv4 or geo.ipv6 or 'No se pudo resolver'}"
        if geo.ipv4 and geo.ipv6:
            ip_line = f"IPv4: {geo.ipv4}  |  IPv6: {geo.ipv6}"

        if not geo.ipv4 and not geo.ipv6:
            # Ni siquiera se pudo resolver una IP: no tiene sentido hablar
            # de geolocalización, el error real es de resolución DNS/IP.
            geo_desc = geo.error or ip_line
            geo_status = "critical"
        elif geo.error:
            # La IP sí se resolvió; lo que falló fue la consulta a los
            # proveedores de geolocalización. Mostramos ambas cosas.
            geo_desc = f"{ip_line}\n{geo.error}"
            geo_status = "warning"
        else:
            geo_desc = (
                f"{ip_line}\n"
                f"País: {geo.country or '—'} | Ciudad: {geo.city or '—'}\n"
                f"ISP: {geo.isp or '—'}"
            )
            geo_status = "neutral"

        cards.append(ResultCard(
            parent, "📍", "IP y Geolocalización", geo_desc,
            status=geo_status, card_color=card_color, accent_color=accent
        ))

        # Encabezados HTTP
        hd = result.headers
        if hd.error:
            hd_desc = hd.error
        else:
            missing = [k for k, v in hd.security_headers.items() if not v]
            hd_desc = f"Estado: {hd.status_code} ({hd.status_meaning})\nServidor: {hd.server or '—'}\n"
            hd_desc += f"Headers ausentes: {len(missing)}/5" if missing else "Todos los headers clave presentes."
        cards.append(ResultCard(
            parent, "🛡", "Encabezados HTTP", hd_desc,
            status=ResultCard.status_from_bool(not hd.error and len([k for k, v in hd.security_headers.items() if not v]) <= 1, warn_only=True),
            card_color=card_color, accent_color=accent
        ))

        # HTTPS
        https_desc = "El sitio utiliza HTTPS correctamente." if hd.uses_https else "El sitio NO utiliza HTTPS."
        cards.append(ResultCard(
            parent, "🔐", "Conexión HTTPS", https_desc,
            status=ResultCard.status_from_bool(hd.uses_https),
            card_color=card_color, accent_color=accent
        ))

        return cards

    # ------------------------------------------------------------------ #
    # Historial y exportación
    # ------------------------------------------------------------------ #
    def _save_to_history(self, result):
        now = datetime.now()
        ip = result.geo.ipv4 or result.geo.ipv6 or ""
        db.insert_record(
            fecha=now.strftime("%Y-%m-%d"),
            hora=now.strftime("%H:%M:%S"),
            url=result.normalized_url,
            ip=ip,
            puntaje=result.risk.score,
            nivel=result.risk.level,
            pais=result.geo.country or "",
            estado_http=result.headers.status_code,
            detalle=result.to_dict(),
        )

    def _export_current(self, fmt):
        if not self.current_result:
            return
        data = self.current_result.to_dict()
        try:
            if fmt == "pdf":
                path = exporter.export_pdf(data)
            elif fmt == "json":
                path = exporter.export_json(data)
            elif fmt == "csv":
                path = exporter.export_csv([self._flatten_for_csv(data)])
            else:
                path = exporter.export_html(data)
            messagebox.showinfo("PhishScope", f"Exportado correctamente:\n{path}")
        except Exception as e:
            messagebox.showerror("PhishScope", f"No se pudo exportar: {e}")

    @staticmethod
    def _flatten_for_csv(data, prefix=""):
        flat = {}
        for key, value in data.items():
            label = f"{prefix}{key}"
            if isinstance(value, dict):
                flat.update(AnalyzerPage._flatten_for_csv(value, prefix=f"{label}."))
            elif isinstance(value, list):
                flat[label] = "; ".join(str(v) for v in value)
            else:
                flat[label] = value
        return flat
