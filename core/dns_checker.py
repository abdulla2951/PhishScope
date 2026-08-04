"""
core/dns_checker.py
---------------------
Resuelve registros DNS (A, AAAA, MX, NS, TXT) de un dominio usando dnspython.
"""

import dns.resolver
from utils.logger import get_logger

logger = get_logger(__name__)

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT"]


class DNSCheckResult:
    """Contenedor de resultado de la resolución DNS."""

    def __init__(self):
        self.records = {rtype: [] for rtype in RECORD_TYPES}
        self.errors = {}

    def to_dict(self):
        return {"records": self.records, "errors": self.errors}


def check_dns(domain: str, timeout: float = 5.0) -> DNSCheckResult:
    """
    Consulta los registros DNS estándar de un dominio.

    Args:
        domain: dominio a resolver.
        timeout: tiempo máximo por consulta en segundos.

    Returns:
        DNSCheckResult con los registros encontrados y errores por tipo.
    """
    result = DNSCheckResult()
    resolver = dns.resolver.Resolver()
    resolver.timeout = timeout
    resolver.lifetime = timeout

    for rtype in RECORD_TYPES:
        try:
            answers = resolver.resolve(domain, rtype)
            values = []
            for rdata in answers:
                if rtype == "MX":
                    values.append(f"{rdata.preference} {rdata.exchange}")
                elif rtype == "TXT":
                    values.append(b"".join(rdata.strings).decode("utf-8", errors="replace"))
                else:
                    values.append(str(rdata))
            result.records[rtype] = values
        except dns.resolver.NoAnswer:
            result.records[rtype] = []
        except dns.resolver.NXDOMAIN:
            result.errors[rtype] = "El dominio no existe (NXDOMAIN)."
            break
        except Exception as e:
            result.errors[rtype] = str(e)
            logger.warning(f"Error DNS ({rtype}) para {domain}: {e}")

    return result
