"""
gui/widgets/risk_gauge.py
----------------------------
Medidor circular de riesgo dibujado sobre un Canvas de tkinter estándar
(CustomTkinter no incluye un widget Canvas propio), con animación suave
de "barrido" al mostrar un nuevo puntaje.
"""

import tkinter as tk
import customtkinter as ctk


class RiskGauge(ctk.CTkFrame):
    """
    Medidor circular que representa visualmente el puntaje de riesgo (0-100).
    """

    def __init__(self, master, size: int = 220, bg_color: str = "#0b0b0b",
                 track_color: str = "#1c1c1c", **kwargs):
        super().__init__(master, fg_color=bg_color, **kwargs)
        self.size = size
        self.bg_color = bg_color
        self.track_color = track_color
        self._current_angle = 0
        self._target_angle = 0
        self._score = 0
        self._level = "Seguro"
        self._color = "#00e676"
        self._animating = False
        self._animations_enabled = True
        self._after_id = None

        self.canvas = tk.Canvas(
            self, width=size, height=size, bg=bg_color, highlightthickness=0, bd=0
        )
        self.canvas.pack(padx=10, pady=10)

        # NOTA: no llamar a este método "_draw". CTkBaseClass (la clase base
        # de CTkFrame) ya define internamente un método "_draw(self,
        # no_color_updates=False)" que CustomTkinter invoca por su cuenta en
        # eventos internos (cambio de apariencia, escalado, resize, etc.).
        # Sobrescribirlo con una firma distinta provoca el error:
        #   RiskGauge._draw() got an unexpected keyword argument 'no_color_updates'
        # Por eso el método propio se llama "_render_gauge".
        self._render_gauge(0, "#00e676")

        # Si el widget se destruye mientras hay una animación en curso,
        # cancelamos el "after" pendiente para evitar errores en segundo plano.
        self.bind("<Destroy>", self._on_destroy)

    def set_animations_enabled(self, enabled: bool):
        self._animations_enabled = enabled

    def _on_destroy(self, event):
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

    def _render_gauge(self, angle: float, color: str):
        self.canvas.delete("all")
        padding = 18
        x0, y0 = padding, padding
        x1, y1 = self.size - padding, self.size - padding

        # Pista de fondo (círculo completo tenue)
        self.canvas.create_oval(x0, y0, x1, y1, outline=self.track_color, width=14)

        # Arco de progreso (empieza arriba, sentido horario)
        if angle > 0:
            self.canvas.create_arc(
                x0, y0, x1, y1,
                start=90, extent=-angle,
                style="arc", outline=color, width=14
            )

        # Texto central: puntaje y nivel
        cx, cy = self.size / 2, self.size / 2
        self.canvas.create_text(
            cx, cy - 10, text=str(int(self._score)),
            fill="#ffffff", font=("Segoe UI", 34, "bold")
        )
        self.canvas.create_text(
            cx, cy + 24, text=self._level,
            fill=color, font=("Segoe UI", 13, "bold")
        )

    def set_score(self, score: int, level: str, color: str):
        """Actualiza el medidor a un nuevo puntaje, animando el barrido si aplica."""
        self._score = score
        self._level = level
        self._color = color
        target_angle = (score / 100) * 360

        if not self._animations_enabled:
            self._current_angle = target_angle
            self._render_gauge(target_angle, color)
            return

        self._target_angle = target_angle
        if not self._animating:
            self._animating = True
            self._animate_step()

    def _animate_step(self):
        # Si el canvas ya no existe (widget destruido a mitad de animación),
        # detenemos silenciosamente en lugar de lanzar un TclError.
        if not self.winfo_exists():
            self._animating = False
            return

        diff = self._target_angle - self._current_angle
        if abs(diff) < 1.5:
            self._current_angle = self._target_angle
            self._render_gauge(self._current_angle, self._color)
            self._animating = False
            self._after_id = None
            return

        self._current_angle += diff * 0.18
        self._render_gauge(self._current_angle, self._color)
        self._after_id = self.after(16, self._animate_step)
