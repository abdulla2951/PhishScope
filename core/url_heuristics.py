"""
core/url_heuristics.py
-------------------------
Analiza la estructura léxica de una URL en busca de patrones sospechosos
comúnmente asociados a phishing: uso de IP en lugar de dominio, caracteres
especiales, punycode, longitud excesiva, subdominios excesivos, etc.

Este módulo es puramente analítico: solo examina el texto de la URL
proporcionada por el usuario, sin realizar ninguna acción sobre terceros.
"""

import re
import ipaddress
import tldextract
from utils.logger import get_logger

logger = get_logger(__name__)

SUSPICIOUS_CHARS = ["@", "%", "//"]
LONG_URL_THRESHOLD = 75
MANY_HYPHENS_THRESHOLD = 4
MANY_DIGITS_THRESHOLD = 5
MANY_SUBDOMAINS_THRESHOLD = 3


class URLHeuristicsResult:
    """Contenedor de resultado del análisis léxico de la URL."""

    def __init__(self):
        self.url_length = 0
        self.is_long_url = False
        self.uses_ip_address = False
        self.has_at_symbol = False
        self.has_percent_encoding = False
        self.has_double_slash_in_path = False
        self.hyphen_count = 0
        self.has_many_hyphens = False
        self.digit_count = 0
        self.has_many_digits = False
        self.is_punycode = False
        self.has_suspicious_unicode = False
        self.subdomain_count = 0
        self.has_excessive_subdomains = False
        self.suspicious_flags = []   # lista legible de hallazgos

    def to_dict(self):
        return {
            "url_length": self.url_length,
            "is_long_url": self.is_long_url,
            "uses_ip_address": self.uses_ip_address,
            "has_at_symbol": self.has_at_symbol,
            "has_percent_encoding": self.has_percent_encoding,
            "has_double_slash_in_path": self.has_double_slash_in_path,
            "hyphen_count": self.hyphen_count,
            "has_many_hyphens": self.has_many_hyphens,
            "digit_count": self.digit_count,
            "has_many_digits": self.has_many_digits,
            "is_punycode": self.is_punycode,
            "has_suspicious_unicode": self.has_suspicious_unicode,
            "subdomain_count": self.subdomain_count,
            "has_excessive_subdomains": self.has_excessive_subdomains,
            "suspicious_flags": self.suspicious_flags,
        }


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def analyze_url_structure(url: str) -> URLHeuristicsResult:
    """
    Analiza la estructura textual de una URL en busca de indicadores de riesgo.

    Args:
        url: URL completa proporcionada por el usuario.

    Returns:
        URLHeuristicsResult con las banderas detectadas.
    """
    result = URLHeuristicsResult()

    result.url_length = len(url)
    result.is_long_url = result.url_length > LONG_URL_THRESHOLD
    if result.is_long_url:
        result.suspicious_flags.append("La URL es inusualmente larga.")

    extracted = tldextract.extract(url)
    host = ".".join(part for part in [extracted.subdomain, extracted.domain, extracted.suffix] if part)

    if _is_ip(extracted.domain) or _is_ip(host):
        result.uses_ip_address = True
        result.suspicious_flags.append("Se usa una dirección IP en lugar de un nombre de dominio.")

    if "@" in url:
        result.has_at_symbol = True
        result.suspicious_flags.append("Contiene el símbolo '@', usado para ofuscar el destino real.")

    if "%" in url:
        result.has_percent_encoding = True
        result.suspicious_flags.append("Contiene codificación porcentual (%), posible ofuscación.")

    # doble barra fuera del esquema (http:// o https://) suele indicar redirección oculta
    scheme_stripped = re.sub(r"^[a-zA-Z]+://", "", url)
    if "//" in scheme_stripped:
        result.has_double_slash_in_path = True
        result.suspicious_flags.append("Contiene '//' fuera del esquema, posible redirección oculta.")

    result.hyphen_count = url.count("-")
    result.has_many_hyphens = result.hyphen_count > MANY_HYPHENS_THRESHOLD
    if result.has_many_hyphens:
        result.suspicious_flags.append("Contiene un número elevado de guiones.")

    result.digit_count = sum(c.isdigit() for c in url)
    result.has_many_digits = result.digit_count > MANY_DIGITS_THRESHOLD
    if result.has_many_digits:
        result.suspicious_flags.append("Contiene un número elevado de dígitos.")

    if "xn--" in url.lower():
        result.is_punycode = True
        result.suspicious_flags.append("Usa codificación punycode (xn--), posible suplantación de caracteres.")

    try:
        url.encode("ascii")
    except UnicodeEncodeError:
        result.has_suspicious_unicode = True
        result.suspicious_flags.append("Contiene caracteres Unicode no estándar.")

    subdomain_parts = [p for p in extracted.subdomain.split(".") if p] if extracted.subdomain else []
    result.subdomain_count = len(subdomain_parts)
    result.has_excessive_subdomains = result.subdomain_count > MANY_SUBDOMAINS_THRESHOLD
    if result.has_excessive_subdomains:
        result.suspicious_flags.append("Tiene un número excesivo de subdominios.")

    return result
