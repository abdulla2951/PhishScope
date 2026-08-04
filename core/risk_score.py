"""
core/risk_score.py
---------------------
Sistema propio de puntuación de riesgo (0-100). Combina los resultados de
todos los analizadores en un único puntaje y nivel de riesgo.

Niveles:
    0  - 24  : Seguro   (verde)
    25 - 49  : Medio    (amarillo)
    50 - 74  : Alto     (naranja)
    75 - 100 : Crítico  (rojo)
"""

from dataclasses import dataclass, field


@dataclass
class RiskFactor:
    """Un factor individual que contribuye al puntaje final."""
    label: str
    points: int
    triggered: bool


@dataclass
class RiskScoreResult:
    score: int = 0
    level: str = "Seguro"
    color: str = "#00e676"
    factors: list = field(default_factory=list)

    def to_dict(self):
        return {
            "score": self.score,
            "level": self.level,
            "color": self.color,
            "factors": [
                {"label": f.label, "points": f.points, "triggered": f.triggered}
                for f in self.factors
            ],
        }


# (etiqueta, puntos si se activa)
WEIGHTS = {
    "ssl_invalid": ("Certificado SSL inválido o ausente", 20),
    "no_https": ("El sitio no utiliza HTTPS", 15),
    "new_domain": ("Dominio registrado hace menos de 6 meses", 15),
    "uses_ip": ("La URL usa una IP en lugar de un dominio", 15),
    "many_symbols": ("Estructura de URL con símbolos/caracteres sospechosos", 10),
    "punycode": ("Uso de punycode (posible homógrafo)", 10),
    "many_redirects": ("Cadena de redirecciones extensa (3+ saltos)", 10),
    "insecure_headers": ("Faltan encabezados de seguridad HTTP clave", 10),
    "bad_status": ("Código de estado HTTP de error", 5),
    "long_url": ("URL inusualmente larga", 5),
    "excessive_subdomains": ("Número excesivo de subdominios", 5),
}


def _level_for_score(score: int):
    if score >= 75:
        return "Crítico", "#ff1744"
    if score >= 50:
        return "Alto", "#ff9100"
    if score >= 25:
        return "Medio", "#ffd600"
    return "Seguro", "#00e676"


def calculate_risk_score(
    ssl_result=None,
    domain_result=None,
    url_heuristics_result=None,
    redirect_result=None,
    header_result=None,
) -> RiskScoreResult:
    """
    Calcula el puntaje de riesgo combinando los resultados de los distintos
    analizadores. Cualquier resultado puede ser None si esa fase falló o no
    se ejecutó; en ese caso simplemente no aporta puntos por ese factor.

    Returns:
        RiskScoreResult con el puntaje total, nivel, color y desglose.
    """
    result = RiskScoreResult()
    total = 0

    def add(key, triggered):
        nonlocal total
        label, points = WEIGHTS[key]
        if triggered:
            total += points
        result.factors.append(RiskFactor(label=label, points=points, triggered=bool(triggered)))

    # SSL / HTTPS
    if ssl_result is not None:
        add("ssl_invalid", not ssl_result.valid)
    if header_result is not None:
        add("no_https", not header_result.uses_https)

    # Dominio
    if domain_result is not None and domain_result.domain_age_days is not None:
        add("new_domain", domain_result.domain_age_days < 180)
    elif domain_result is not None:
        add("new_domain", False)

    # Heurísticas léxicas de la URL
    if url_heuristics_result is not None:
        add("uses_ip", url_heuristics_result.uses_ip_address)
        symbol_flags = (
            url_heuristics_result.has_at_symbol
            or url_heuristics_result.has_percent_encoding
            or url_heuristics_result.has_double_slash_in_path
            or url_heuristics_result.has_many_hyphens
            or url_heuristics_result.has_many_digits
            or url_heuristics_result.has_suspicious_unicode
        )
        add("many_symbols", symbol_flags)
        add("punycode", url_heuristics_result.is_punycode)
        add("long_url", url_heuristics_result.is_long_url)
        add("excessive_subdomains", url_heuristics_result.has_excessive_subdomains)

    # Redirecciones
    if redirect_result is not None:
        add("many_redirects", redirect_result.redirect_count >= 3)

    # Encabezados / estado HTTP
    if header_result is not None:
        missing_headers = sum(
            1 for v in header_result.security_headers.values() if not v
        )
        add("insecure_headers", missing_headers >= 3)
        add("bad_status", header_result.status_code is not None and header_result.status_code >= 400)

    total = min(total, 100)
    result.score = total
    result.level, result.color = _level_for_score(total)

    return result
