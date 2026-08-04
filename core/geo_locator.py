"""
core/geo_locator.py
---------------------
Resuelve la IP (v4/v6) de un dominio, realiza reverse DNS y obtiene
geolocalización aproximada (país, ciudad, ASN, ISP) mediante servicios
públicos de IP info. Solo se consulta la IP resultante de la resolución
del dominio proporcionado por el usuario; no se escanean ni contactan
terceros ajenos a esa resolución.

Se prueban varios proveedores gratuitos en cadena porque todos tienen
límites de uso estrictos (por minuto/día) y es común recibir HTTP 429
("Too Many Requests") incluso con un uso normal de la app. Si un
proveedor está saturado o no responde, se intenta el siguiente antes
de reportar un error al usuario.
"""

import socket
import requests
from utils.logger import get_logger

logger = get_logger(__name__)

HEADERS = {"User-Agent": "PhishScope/1.0 (+https://github.com/phishscope)"}


def _fetch_ipapi_co(ip: str, timeout: float):
    """https://ipapi.co — JSON, ~1000 peticiones/día en el plan gratuito."""
    resp = requests.get(f"https://ipapi.co/{ip}/json/", headers=HEADERS, timeout=timeout)
    if resp.status_code == 429:
        return None, "rate_limited"
    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}"
    data = resp.json()
    if data.get("error"):
        return None, data.get("reason", "error del proveedor")
    return {
        "country": data.get("country_name"),
        "city": data.get("city"),
        "asn": data.get("asn"),
        "isp": data.get("org"),
    }, None


def _fetch_ipwho_is(ip: str, timeout: float):
    """https://ipwho.is — sin API key, sin límite estricto documentado."""
    resp = requests.get(f"https://ipwho.is/{ip}", headers=HEADERS, timeout=timeout)
    if resp.status_code == 429:
        return None, "rate_limited"
    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}"
    data = resp.json()
    if not data.get("success", True):
        return None, data.get("message", "error del proveedor")
    connection = data.get("connection") or {}
    return {
        "country": data.get("country"),
        "city": data.get("city"),
        "asn": connection.get("asn"),
        "isp": connection.get("isp") or connection.get("org"),
    }, None


def _fetch_ip_api_com(ip: str, timeout: float):
    """http://ip-api.com — 45 peticiones/minuto en el plan gratuito (sin HTTPS)."""
    resp = requests.get(
        f"http://ip-api.com/json/{ip}?fields=status,message,country,city,as,isp",
        headers=HEADERS, timeout=timeout,
    )
    if resp.status_code == 429:
        return None, "rate_limited"
    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}"
    data = resp.json()
    if data.get("status") != "success":
        return None, data.get("message", "error del proveedor")
    return {
        "country": data.get("country"),
        "city": data.get("city"),
        "asn": data.get("as"),
        "isp": data.get("isp"),
    }, None


# Orden de intento: si un proveedor está saturado (429) o falla, se prueba
# el siguiente automáticamente antes de darle un error al usuario.
GEO_PROVIDERS = [
    ("ipapi.co", _fetch_ipapi_co),
    ("ipwho.is", _fetch_ipwho_is),
    ("ip-api.com", _fetch_ip_api_com),
]


class GeoResult:
    """Contenedor de resultado de IP + geolocalización."""

    def __init__(self):
        self.ipv4 = None
        self.ipv6 = None
        self.reverse_dns = None
        self.country = None
        self.city = None
        self.asn = None
        self.isp = None
        self.error = None

    def to_dict(self):
        return {
            "ipv4": self.ipv4,
            "ipv6": self.ipv6,
            "reverse_dns": self.reverse_dns,
            "country": self.country,
            "city": self.city,
            "asn": self.asn,
            "isp": self.isp,
            "error": self.error,
        }


def resolve_ips(domain: str) -> tuple[str | None, str | None]:
    """Resuelve IPv4 e IPv6 de un dominio."""
    ipv4, ipv6 = None, None
    try:
        infos = socket.getaddrinfo(domain, None)
        for family, _, _, _, sockaddr in infos:
            if family == socket.AF_INET and not ipv4:
                ipv4 = sockaddr[0]
            elif family == socket.AF_INET6 and not ipv6:
                ipv6 = sockaddr[0]
    except socket.gaierror as e:
        logger.warning(f"No se pudo resolver la IP de {domain}: {e}")
    return ipv4, ipv6


def reverse_dns_lookup(ip: str) -> str | None:
    """Obtiene el hostname asociado a una IP mediante reverse DNS."""
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except (socket.herror, socket.gaierror):
        return None


def _fetch_geo_info(target_ip: str, timeout: float):
    """
    Intenta obtener la geolocalización probando cada proveedor en orden.
    Devuelve (datos, error). Si todos fallan, datos es None y error trae
    un resumen legible de lo ocurrido con cada proveedor.
    """
    failures = []
    for name, fetch in GEO_PROVIDERS:
        try:
            data, err = fetch(target_ip, timeout)
        except requests.Timeout:
            failures.append(f"{name}: tiempo de espera agotado")
            continue
        except requests.RequestException as e:
            failures.append(f"{name}: {e}")
            continue

        if data is not None:
            return data, None

        reason = "límite de solicitudes alcanzado" if err == "rate_limited" else err
        failures.append(f"{name}: {reason}")
        logger.warning(f"Proveedor de geolocalización '{name}' falló para {target_ip}: {reason}")

    summary = "; ".join(failures)
    return None, f"Todos los servicios de geolocalización fallaron o alcanzaron su límite de uso ({summary})."


def check_geo(domain: str, timeout: float = 6.0) -> GeoResult:
    """
    Resuelve IP, reverse DNS y geolocalización aproximada para un dominio,
    probando varios proveedores gratuitos por si alguno está saturado.

    Args:
        domain: dominio a analizar.
        timeout: tiempo máximo por petición de geolocalización.

    Returns:
        GeoResult con los datos disponibles.
    """
    result = GeoResult()
    ipv4, ipv6 = resolve_ips(domain)
    result.ipv4 = ipv4
    result.ipv6 = ipv6

    target_ip = ipv4 or ipv6
    if not target_ip:
        result.error = "No se pudo resolver ninguna dirección IP para este dominio."
        return result

    result.reverse_dns = reverse_dns_lookup(target_ip)

    data, error = _fetch_geo_info(target_ip, timeout)
    if data:
        result.country = data.get("country")
        result.city = data.get("city")
        result.asn = data.get("asn")
        result.isp = data.get("isp")
    else:
        result.error = error

    return result
