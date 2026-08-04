<div align="center">

<img src="assets/logo.png" alt="PhishScope" width="120"/>

# PhishScope

**Análisis defensivo de URLs y detección de phishing**

![Versión](https://img.shields.io/badge/versi%C3%B3n-1.0.0-38bdf8)
![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB)
![Plataforma](https://img.shields.io/badge/Windows-11-0078D6)
![Licencia](https://img.shields.io/badge/Licencia-MIT-00c853)

*Desarrollado por [zieragk](https://github.com/zieragk)*

</div>

---

PhishScope es una aplicación de escritorio para el **análisis defensivo de
URLs**. Evalúa indicadores de phishing y de configuración insegura y los
combina en un **puntaje de riesgo** propio de 0 a 100, presentado con un
medidor visual y tarjetas de resultado detalladas.

> Esta herramienta analiza **únicamente** URLs proporcionadas por el usuario.
> No incluye funciones ofensivas ni automatiza ataques contra terceros.

## Características

- **Certificados SSL/TLS**: validez, emisor, versión TLS y días hasta expiración.
- **Información del dominio**: datos WHOIS, antigüedad del registro y registrador.
- **Registros DNS**: consulta A, AAAA, MX, NS y TXT del dominio.
- **IP y geolocalización**: resolución IPv4/IPv6, país, ciudad e ISP.
- **Cadenas de redirección**: número de saltos y URL de destino final.
- **Encabezados de seguridad HTTP**: evaluación de headers clave (HSTS, CSP, etc.).
- **Patrones léxicos de phishing**: heurística sobre la estructura de la URL.
- **Puntaje de riesgo consolidado** con medidor animado y nivel (Seguro/Medio/Alto/Crítico).
- **Historial persistente** en SQLite con búsqueda y exportación.
- **Exportación** a PDF, JSON, CSV y HTML.
- **Tema oscuro personalizable** (colores de fondo, acento y tarjetas).

## Capturas

La interfaz incluye una barra lateral con logo, página de bienvenida con
estadísticas, un analizador con medidor circular de riesgo, historial con
búsqueda y página de configuración con cambio de colores.

## Descarga e instalación

### Opción A: ejecutable (Windows)

1. Descarga la última versión de **`PhishScope.exe`** desde la sección
   [Releases](https://github.com/zieragk/phishscope/releases).
2. Ejecuta el archivo: no requiere instalación.
3. La primera vez crea junto al ejecutable las carpetas `config/`,
   `database/`, `export/` y `logs/` donde persiste su información.

> Windows SmartScreen puede mostrar una advertencia: selecciona
> *Más información > Ejecutar de todas formas*.

### Opción B: desde el código fuente

Requisitos: **Python 3.13 o superior**.

```bash
# Clonar el repositorio
git clone https://github.com/zieragk/phishscope.git
cd phishscope

# Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# Instalar dependencias e iniciar
pip install -r requirements.txt
python main.py
```

## Uso

1. Abre la pestaña **Analizador de URLs**.
2. Pega una URL (por ejemplo `https://ejemplo.com`) y presiona **Analizar**.
3. Espera mientras se ejecutan los análisis en segundo plano (la barra de
   progreso indica cada paso).
4. Revisa el **puntaje de riesgo** y las tarjetas por sección.
5. Exporta el resultado a PDF, JSON, CSV o HTML, o déjalo en el historial.

## Compilar el ejecutable

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "PhishScope" ^
    --icon "assets\icon.ico" --add-data "assets;assets" main.py
```

El ejecutable quedará en `dist/PhishScope.exe`.

## Estructura del proyecto

```
PhishScope/
├── main.py                # Punto de entrada
├── requirements.txt
├── assets/                # Logo e iconos
├── core/                  # Lógica de análisis (SSL, WHOIS, DNS, riesgo, etc.)
├── database/              # Persistencia SQLite del historial
├── export/                # Exportación a PDF / JSON / CSV / HTML
├── gui/                   # Interfaz gráfica (CustomTkinter)
│   ├── pages/             # Páginas: Inicio, Analizador, Historial, etc.
│   └── widgets/           # Componentes reutilizables (gauge, tarjetas)
├── modules/               # Base para futuras herramientas de la suite PhishScope
├── utils/                 # Configuración, logging, constantes, rutas
└── logs/                  # app.log (rotativo)
```

## Tecnologías

Python 3.13 · CustomTkinter · ttkbootstrap · requests · cryptography ·
python-whois · dnspython · tldextract · validators · Pillow · SQLite ·
reportlab · PyInstaller

## Aviso legal

PhishScope es una herramienta **defensiva** de análisis. Úsala únicamente
sobre URLs que te pertenezcan o cuya revisión esté autorizada. Los datos
obtenidos de servicios externos (WHOIS, geolocalización, DNS) son
aproximados y pueden variar según el proveedor.

## Licencia

Distribuido bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE).
