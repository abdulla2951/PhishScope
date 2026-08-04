"""
core/redirect_checker.py
--------------------------
Sigue la cadena de redirecciones HTTP de una URL y reporta el destino
final, la cantidad de saltos y la cadena completa recorrida.
"""

import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class RedirectResult:
    """Contenedor de resultado del análisis de redirecciones."""

    def __init__(self):
        self.chain = []          # lista de URLs visitadas en orden
        self.final_url = None
        self.redirect_count = 0
        self.final_status_code = None
        self.error = None

    def to_dict(self):
        return {
            "chain": self.chain,
            "final_url": self.final_url,
            "redirect_count": self.redirect_count,
            "final_status_code": self.final_status_code,
            "error": self.error,
        }


def check_redirects(url: str, timeout: float = 8.0, max_redirects: int = 15) -> RedirectResult:
    """
    Sigue la cadena de redirecciones de una URL con requests.

    Args:
        url: URL inicial a analizar.
        timeout: tiempo máximo por petición.
        max_redirects: límite de saltos permitidos.

    Returns:
        RedirectResult con la cadena completa y el destino final.
    """
    result = RedirectResult()
    headers = {"User-Agent": "PhishScope/1.0 (+security-analysis)"}

    try:
        resp = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
            stream=True,
        )
        resp.close()

        result.chain = [r.url for r in resp.history] + [resp.url]
        result.redirect_count = len(resp.history)
        result.final_url = resp.url
        result.final_status_code = resp.status_code

        if len(resp.history) > max_redirects:
            result.error = "Se alcanzó el límite de redirecciones permitidas."

    except requests.TooManyRedirects:
        result.error = "Demasiadas redirecciones (posible bucle)."
        logger.warning(f"Demasiadas redirecciones para {url}")
    except requests.RequestException as e:
        result.error = f"No se pudo seguir la cadena de redirecciones: {e}"
        logger.warning(f"Error de redirección para {url}: {e}")

    return result
