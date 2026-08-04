"""
modules/base_tool.py
----------------------
Clase base para futuras herramientas de la suite de ciberseguridad PhishScope
(escáner de puertos, analizador de hashes, utilidades DNS/WHOIS, etc.).

Cada nueva herramienta debe:
    1. Heredar de BaseTool.
    2. Implementar `run(self, *args, **kwargs)`.
    3. Registrarse en el sidebar (gui/sidebar.py) y en PhishScopeApp.pages
       (gui/app.py) siguiendo el mismo patrón que las páginas existentes.

Este módulo no contiene funciones ofensivas; sirve únicamente como
andamiaje de extensión para herramientas defensivas adicionales.
"""

from abc import ABC, abstractmethod
from utils.logger import get_logger


class BaseTool(ABC):
    """Contrato mínimo que debe cumplir cualquier herramienta de la suite PhishScope."""

    name = "Herramienta sin nombre"
    icon = "🧰"
    description = ""

    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def run(self, *args, **kwargs):
        """Ejecuta la lógica principal de la herramienta y devuelve su resultado."""
        raise NotImplementedError
