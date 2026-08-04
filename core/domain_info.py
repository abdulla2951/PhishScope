"""
core/domain_info.py
----------------------
Obtiene información WHOIS del dominio: fecha de creación, expiración,
registrador y edad del dominio en días.
"""

import whois
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger(__name__)


class DomainInfoResult:
    """Contenedor de resultado de la consulta WHOIS."""

    def __init__(self):
        self.registrar = None
        self.creation_date = None
        self.expiration_date = None
        self.domain_age_days = None
        self.name_servers = []
        self.error = None

    def to_dict(self):
        return {
            "registrar": self.registrar,
            "creation_date": self.creation_date,
            "expiration_date": self.expiration_date,
            "domain_age_days": self.domain_age_days,
            "name_servers": self.name_servers,
            "error": self.error,
        }


def _first_if_list(value):
    """WHOIS a veces devuelve listas de fechas/valores; toma el primero."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _to_naive(dt):
    """Normaliza datetimes con o sin tzinfo para poder restarlos con seguridad."""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def check_domain(domain: str) -> DomainInfoResult:
    """
    Consulta WHOIS para un dominio y calcula su antigüedad.

    Args:
        domain: nombre de dominio (sin esquema ni ruta).

    Returns:
        DomainInfoResult con los datos disponibles.
    """
    result = DomainInfoResult()

    try:
        data = whois.whois(domain)

        result.registrar = _first_if_list(data.registrar)

        creation = _to_naive(_first_if_list(data.creation_date))
        expiration = _to_naive(_first_if_list(data.expiration_date))

        result.creation_date = creation.strftime("%Y-%m-%d") if creation else None
        result.expiration_date = expiration.strftime("%Y-%m-%d") if expiration else None

        if creation:
            delta = datetime.utcnow() - creation
            result.domain_age_days = max(delta.days, 0)

        ns = data.name_servers
        if ns:
            result.name_servers = [n.lower() for n in ns] if isinstance(ns, list) else [str(ns).lower()]

        if not result.creation_date and not result.registrar:
            result.error = "WHOIS no devolvió información útil para este dominio."

    except Exception as e:
        result.error = f"No se pudo obtener información WHOIS: {e}"
        logger.warning(f"Error WHOIS para {domain}: {e}")

    return result
