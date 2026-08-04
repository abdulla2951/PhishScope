"""
main.py
---------
Punto de entrada de PhishScope.

Ejecutar con:
    python main.py

Compilar a ejecutable único con PyInstaller:
    pyinstaller --noconfirm --onefile --windowed --name "PhishScope" ^
        --add-data "assets;assets" main.py
"""

import sys
import traceback

from utils.logger import get_logger

logger = get_logger("main")


def main():
    try:
        from gui.app import run_app
        run_app()
    except Exception:
        logger.error("Error fatal no controlado:\n" + traceback.format_exc())
        raise


if __name__ == "__main__":
    sys.exit(main() or 0)
