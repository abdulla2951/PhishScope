"""
utils/validators.py
---------------------
Funciones de validación y normalización de URLs de entrada.
"""

import re
import validators as validators_lib
from urllib.parse import urlparse


def normalize_url(raw_url: str) -> str:
    """Añade esquema https:// si el usuario no lo incluyó."""
    raw_url = raw_url.strip()
    if not re.match(r"^[a-zA-Z]+://", raw_url):
        raw_url = "https://" + raw_url
    return raw_url


def is_valid_url(url: str) -> bool:
    """Valida que la cadena tenga un formato de URL correcto."""
    try:
        return bool(validators_lib.url(url))
    except Exception:
        return False


def get_domain(url: str) -> str:
    """Extrae el dominio (netloc) de una URL, sin puerto ni credenciales."""
    parsed = urlparse(url)
    host = parsed.hostname or ""
    return host
