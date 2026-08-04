"""
core/url_analyzer.py
-----------------------
Orquesta todos los módulos de análisis (SSL, WHOIS, DNS, geolocalización,
redirecciones, encabezados y heurísticas léxicas) para producir un
resultado consolidado de una única URL, incluyendo el puntaje de riesgo.
"""

from datetime import datetime

from core import ssl_checker, domain_info, dns_checker, geo_locator
from core import redirect_checker, header_checker, url_heuristics, risk_score
from utils.validators import normalize_url, is_valid_url, get_domain
from utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisResult:
    """Resultado consolidado de analizar una URL."""

    def __init__(self, original_url: str):
        self.original_url = original_url
        self.normalized_url = None
        self.domain = None
        self.timestamp = datetime.now().isoformat(timespec="seconds")

        self.url_heuristics = None
        self.ssl = None
        self.domain_info = None
        self.dns = None
        self.geo = None
        self.redirects = None
        self.headers = None
        self.risk = None

        self.valid_input = True
        self.input_error = None

    def to_dict(self):
        return {
            "original_url": self.original_url,
            "normalized_url": self.normalized_url,
            "domain": self.domain,
            "timestamp": self.timestamp,
            "url_heuristics": self.url_heuristics.to_dict() if self.url_heuristics else None,
            "ssl": self.ssl.to_dict() if self.ssl else None,
            "domain_info": self.domain_info.to_dict() if self.domain_info else None,
            "dns": self.dns.to_dict() if self.dns else None,
            "geo": self.geo.to_dict() if self.geo else None,
            "redirects": self.redirects.to_dict() if self.redirects else None,
            "headers": self.headers.to_dict() if self.headers else None,
            "risk": self.risk.to_dict() if self.risk else None,
        }


def analyze(url_input: str, progress_callback=None) -> AnalysisResult:
    """
    Ejecuta el análisis completo de una URL proporcionada por el usuario.

    Args:
        url_input: texto ingresado por el usuario (con o sin esquema).
        progress_callback: función opcional callback(str) para reportar
            el paso actual del análisis a la interfaz gráfica.

    Returns:
        AnalysisResult con todos los sub-resultados y el puntaje de riesgo.
    """
    def report(step):
        if progress_callback:
            try:
                progress_callback(step)
            except Exception:
                pass

    result = AnalysisResult(url_input)
    normalized = normalize_url(url_input)
    result.normalized_url = normalized

    if not is_valid_url(normalized):
        result.valid_input = False
        result.input_error = "La URL proporcionada no tiene un formato válido."
        logger.warning(f"URL inválida proporcionada: {url_input}")
        return result

    domain = get_domain(normalized)
    result.domain = domain

    report("Analizando estructura de la URL...")
    result.url_heuristics = url_heuristics.analyze_url_structure(normalized)

    report("Verificando certificado SSL/TLS...")
    result.ssl = ssl_checker.check_ssl(domain)

    report("Consultando información WHOIS...")
    result.domain_info = domain_info.check_domain(domain)

    report("Resolviendo registros DNS...")
    result.dns = dns_checker.check_dns(domain)

    report("Geolocalizando dirección IP...")
    result.geo = geo_locator.check_geo(domain)

    report("Siguiendo cadena de redirecciones...")
    result.redirects = redirect_checker.check_redirects(normalized)

    report("Analizando encabezados HTTP...")
    target_for_headers = result.redirects.final_url if result.redirects and result.redirects.final_url else normalized
    result.headers = header_checker.check_headers(target_for_headers)

    report("Calculando puntaje de riesgo...")
    result.risk = risk_score.calculate_risk_score(
        ssl_result=result.ssl,
        domain_result=result.domain_info,
        url_heuristics_result=result.url_heuristics,
        redirect_result=result.redirects,
        header_result=result.headers,
    )

    report("Análisis completo.")
    return result
