"""
core/header_checker.py
-------------------------
Analiza los encabezados de seguridad HTTP de una respuesta y el código
de estado devuelto por el servidor.
"""

import requests
from utils.logger import get_logger

logger = get_logger(__name__)

SECURITY_HEADERS = [
    "Strict-Transport-Security",
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-XSS-Protection",
    "X-Content-Type-Options",
]

STATUS_MEANINGS = {
    200: "OK - Respuesta correcta",
    201: "Creado",
    204: "Sin contenido",
    301: "Redirección permanente",
    302: "Redirección temporal",
    307: "Redirección temporal (método preservado)",
    308: "Redirección permanente (método preservado)",
    400: "Solicitud incorrecta",
    401: "No autorizado",
    403: "Prohibido",
    404: "No encontrado",
    405: "Método no permitido",
    429: "Demasiadas solicitudes",
    500: "Error interno del servidor",
    502: "Bad Gateway",
    503: "Servicio no disponible",
    504: "Tiempo de espera del Gateway agotado",
}


class HeaderCheckResult:
    """Contenedor de resultado del análisis de encabezados y estado."""

    def __init__(self):
        self.status_code = None
        self.status_meaning = None
        self.server = None
        self.content_type = None
        self.security_headers = {}   # header -> valor o None si ausente
        self.uses_https = False
        self.error = None

    def to_dict(self):
        return {
            "status_code": self.status_code,
            "status_meaning": self.status_meaning,
            "server": self.server,
            "content_type": self.content_type,
            "security_headers": self.security_headers,
            "uses_https": self.uses_https,
            "error": self.error,
        }


def check_headers(url: str, timeout: float = 8.0) -> HeaderCheckResult:
    """
    Realiza una petición GET y analiza encabezados de seguridad y estado.

    Args:
        url: URL a consultar (se recomienda pasar la URL final, tras redirecciones).
        timeout: tiempo máximo de espera.

    Returns:
        HeaderCheckResult con los datos obtenidos.
    """
    result = HeaderCheckResult()
    headers = {"User-Agent": "PhishScope/1.0 (+security-analysis)"}

    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)

        result.status_code = resp.status_code
        result.status_meaning = STATUS_MEANINGS.get(resp.status_code, "Código no estándar")
        result.server = resp.headers.get("Server")
        result.content_type = resp.headers.get("Content-Type")
        result.uses_https = resp.url.lower().startswith("https://")

        for h in SECURITY_HEADERS:
            result.security_headers[h] = resp.headers.get(h)

    except requests.RequestException as e:
        result.error = f"No se pudo obtener la respuesta HTTP: {e}"
        logger.warning(f"Error de encabezados para {url}: {e}")

    return result
