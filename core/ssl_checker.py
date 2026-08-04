"""
core/ssl_checker.py
---------------------
Analiza el certificado SSL/TLS de un dominio: validez, emisor, fechas de
vencimiento, versión de protocolo TLS y cipher suite en uso.
"""

import ssl
import socket
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger(__name__)


class SSLCheckResult:
    """Contenedor de resultado del análisis SSL."""

    def __init__(self):
        self.valid = False
        self.issuer = None
        self.subject = None
        self.not_before = None
        self.not_after = None
        self.days_until_expiry = None
        self.tls_version = None
        self.cipher_suite = None
        self.error = None

    def to_dict(self):
        return {
            "valid": self.valid,
            "issuer": self.issuer,
            "subject": self.subject,
            "not_before": self.not_before,
            "not_after": self.not_after,
            "days_until_expiry": self.days_until_expiry,
            "tls_version": self.tls_version,
            "cipher_suite": self.cipher_suite,
            "error": self.error,
        }


def _parse_cert_name(name_tuple_seq):
    """Convierte la estructura de nombre X.509 en un string legible."""
    if not name_tuple_seq:
        return None
    parts = []
    for rdn in name_tuple_seq:
        for key, value in rdn:
            parts.append(f"{key}={value}")
    return ", ".join(parts)


def check_ssl(hostname: str, port: int = 443, timeout: float = 6.0) -> SSLCheckResult:
    """
    Se conecta al host por TLS y extrae información del certificado.

    Args:
        hostname: dominio a analizar (sin esquema).
        port: puerto HTTPS, por defecto 443.
        timeout: tiempo máximo de espera en segundos.

    Returns:
        SSLCheckResult con los datos obtenidos (o el error, si falló).
    """
    result = SSLCheckResult()
    context = ssl.create_default_context()

    try:
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()  # (nombre, versión_protocolo, bits)

                result.valid = True
                result.issuer = _parse_cert_name(cert.get("issuer"))
                result.subject = _parse_cert_name(cert.get("subject"))
                result.not_before = cert.get("notBefore")
                result.not_after = cert.get("notAfter")
                result.tls_version = ssock.version()
                if cipher:
                    result.cipher_suite = cipher[0]

                if result.not_after:
                    try:
                        expiry_dt = datetime.strptime(
                            result.not_after, "%b %d %H:%M:%S %Y %Z"
                        ).replace(tzinfo=timezone.utc)
                        delta = expiry_dt - datetime.now(timezone.utc)
                        result.days_until_expiry = delta.days
                        if delta.days < 0:
                            result.valid = False
                            result.error = "El certificado ha expirado."
                    except ValueError:
                        pass

    except ssl.SSLCertVerificationError as e:
        result.valid = False
        result.error = f"Certificado no verificado: {e}"
        logger.warning(f"SSL no verificado para {hostname}: {e}")
    except (socket.timeout, socket.gaierror, ConnectionRefusedError, OSError) as e:
        result.valid = False
        result.error = f"No se pudo establecer conexión segura: {e}"
        logger.warning(f"Error de conexión SSL para {hostname}: {e}")
    except Exception as e:
        result.valid = False
        result.error = f"Error inesperado analizando SSL: {e}"
        logger.error(f"Error inesperado SSL para {hostname}: {e}")

    return result
