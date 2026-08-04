"""
export/exporter.py
---------------------
Exporta resultados de análisis (individuales o el historial completo) a
PDF, JSON, CSV y HTML.
"""

import json
import csv
import os
from datetime import datetime
from utils.logger import get_logger
from utils.config_manager import config

logger = get_logger(__name__)


def _timestamped_name(prefix: str, extension: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{ts}.{extension}"


def export_json(data, filename: str = None) -> str:
    """Exporta un dict (o lista de dicts) a un archivo JSON."""
    filename = filename or _timestamped_name("phishscope", "json")
    path = os.path.join(config.export_folder, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return path
    except OSError as e:
        logger.error(f"Error exportando JSON: {e}")
        raise


def export_csv(rows: list, filename: str = None) -> str:
    """Exporta una lista de dicts (filas del historial) a CSV."""
    filename = filename or _timestamped_name("phishscope", "csv")
    path = os.path.join(config.export_folder, filename)

    if not rows:
        rows = [{}]

    try:
        fieldnames = list(rows[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return path
    except OSError as e:
        logger.error(f"Error exportando CSV: {e}")
        raise


def _dict_to_html_rows(d: dict, prefix: str = "") -> str:
    """Convierte recursivamente un dict en filas de tabla HTML."""
    html = ""
    for key, value in d.items():
        label = f"{prefix}{key}"
        if isinstance(value, dict):
            html += _dict_to_html_rows(value, prefix=f"{label}.")
        elif isinstance(value, list):
            html += f"<tr><td>{label}</td><td>{', '.join(map(str, value)) or '—'}</td></tr>"
        else:
            display = value if value not in (None, "") else "—"
            html += f"<tr><td>{label}</td><td>{display}</td></tr>"
    return html


def export_html(data: dict, filename: str = None) -> str:
    """Exporta el resultado de un análisis a un reporte HTML con la estética PhishScope."""
    filename = filename or _timestamped_name("phishscope_report", "html")
    path = os.path.join(config.export_folder, filename)

    theme = config.get_theme()
    rows_html = _dict_to_html_rows(data)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>PhishScope - Reporte</title>
<style>
    body {{
        background-color: {theme['bg_color']};
        color: {theme['text_color']};
        font-family: 'Segoe UI', Arial, sans-serif;
        padding: 40px;
    }}
    h1 {{
        color: {theme['accent_color']};
        border-bottom: 2px solid {theme['accent_color']};
        padding-bottom: 10px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }}
    td {{
        padding: 10px 14px;
        border-bottom: 1px solid #222;
        vertical-align: top;
    }}
    td:first-child {{
        color: {theme['accent_color']};
        font-weight: bold;
        width: 35%;
    }}
    .footer {{
        margin-top: 30px;
        color: #666;
        font-size: 12px;
    }}
</style>
</head>
<body>
    <h1>PhishScope — Reporte de Análisis</h1>
    <table>
        {rows_html}
    </table>
    <div class="footer">Generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
</body>
</html>"""

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return path
    except OSError as e:
        logger.error(f"Error exportando HTML: {e}")
        raise


def export_pdf(data: dict, filename: str = None) -> str:
    """
    Exporta el resultado de un análisis a PDF usando reportlab.
    Genera un layout simple de clave/valor con la paleta de colores PhishScope.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor

    filename = filename or _timestamped_name("phishscope_report", "pdf")
    path = os.path.join(config.export_folder, filename)
    theme = config.get_theme()

    bg = HexColor(theme["bg_color"])
    accent = HexColor(theme["accent_color"])
    text_color = HexColor(theme["text_color"])

    try:
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        margin = 20 * mm
        y = height - margin

        def new_page():
            nonlocal y
            c.setFillColor(bg)
            c.rect(0, 0, width, height, fill=1, stroke=0)
            y = height - margin

        new_page()

        c.setFillColor(accent)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(margin, y, "PhishScope — Reporte")
        y -= 12 * mm

        c.setFont("Helvetica", 9)

        def flatten(d, prefix=""):
            items = []
            for key, value in d.items():
                label = f"{prefix}{key}"
                if isinstance(value, dict):
                    items.extend(flatten(value, prefix=f"{label}."))
                elif isinstance(value, list):
                    items.append((label, ", ".join(map(str, value)) or "—"))
                else:
                    items.append((label, str(value) if value not in (None, "") else "—"))
            return items

        for label, value in flatten(data):
            if y < margin + 10 * mm:
                c.showPage()
                new_page()
                c.setFont("Helvetica", 9)

            c.setFillColor(accent)
            c.drawString(margin, y, f"{label}:")
            c.setFillColor(text_color)
            # Recorta valores muy largos para que no se salgan de la página
            value_str = value if len(value) < 90 else value[:87] + "..."
            c.drawString(margin + 65 * mm, y, value_str)
            y -= 6 * mm

        c.save()
        return path
    except Exception as e:
        logger.error(f"Error exportando PDF: {e}")
        raise
