<div align="center">

<img src="assets/logo.png" alt="PhishScope" width="120"/>

# PhishScope

**Free, offline-first URL threat intelligence & phishing detection tool**

![Versión](https://img.shields.io/badge/release-1.0.0-38bdf8)
![Python](https://img.shields.io/badge/Python-3.13%2B-3776AB)
![Platform](https://img.shields.io/badge/Windows-11-0078D6)
![License](https://img.shields.io/badge/License-MIT-00c853)
![PRs](https://img.shields.io/badge/PRs-welcome-ff9f43)

*Built by [Zieragk](https://github.com/Zieragk)*

</div>

---

> **PhishScope is a defensive-only tool.** It analyzes the URLs you paste and
> reports phishing indicators. No offensive features, no automation of attacks
> against third parties.

## Why PhishScope?

Phishing is the #1 entry vector in modern breaches. Most people can't tell a
safe link from a malicious one just by looking at it. **PhishScope does the
work for you**: it inspects a URL across 8 independent dimensions and produces
a single, easy-to-understand **risk score from 0 to 100** — powered by its own
scoring engine, with a live animated gauge and detailed result cards.

## Features

| Area | What it checks |
|------|----------------|
| SSL/TLS certificates | Validity, issuer, TLS version, days to expiry |
| Domain / WHOIS | Registrar, creation date, domain age (young = risk) |
| DNS records | A, AAAA, MX, NS, TXT lookups |
| IP & geolocation | IPv4/IPv6, country, city, ISP |
| Redirects | Number of hops and final destination URL |
| HTTP security headers | HSTS, CSP, X-Frame-Options and more |
| URL structure | Lexical phishing patterns, suspicious flags |
| Risk engine | Consolidated 0-100 score with Seguro/Medio/Alto/Crítico level |

**Plus:** persistent SQLite history with search · export to **PDF / JSON /
CSV / HTML** · dark theme with customizable accent colors · modern
CustomTkinter UI · 100% offline analysis (only WHOIS/geo queries hit external
public services).

## Demo

![PhishScope demo](assets/logo.png)

> *Screenshots coming soon — add your own captures to the `assets/` folder
> and link them here for the best first impression.*

## Installation

### Option A — Windows executable (no install required)

1. Download **`PhishScope.exe`** from the latest
   [Release](https://github.com/Zieragk/PhishScope/releases).
2. Run it. No installation needed — it's fully portable.
3. On first launch it creates `config/`, `database/`, `export/` and `logs/`
   next to the executable to persist your data.

> Windows SmartScreen may warn you: choose *More info > Run anyway*.

### Option B — From source

Requirements: **Python 3.13+**

```bash
git clone https://github.com/Zieragk/PhishScope.git
cd PhishScope

python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

pip install -r requirements.txt
python main.py
```

## Usage

1. Open the **URL Analyzer** tab.
2. Paste a URL (e.g. `https://example.com`) and hit **Analyze**.
3. Watch the live progress while each check runs in the background.
4. Review the **risk score** and per-section result cards.
5. Export the report to PDF, JSON, CSV or HTML, or keep it in history.

## Build the executable yourself

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "PhishScope" ^
    --icon "assets\icon.ico" --add-data "assets;assets" main.py
```

The binary will be at `dist/PhishScope.exe`.

## Project structure

```
PhishScope/
├── main.py                # Entry point
├── requirements.txt
├── assets/                # Logo & icons
├── core/                  # Analysis logic (SSL, WHOIS, DNS, risk, etc.)
├── database/              # SQLite history persistence
├── export/                # PDF / JSON / CSV / HTML exporters
├── gui/                   # CustomTkinter interface
│   ├── pages/             # Home, Analyzer, History, Settings, etc.
│   └── widgets/           # Reusable components (gauge, cards)
├── modules/               # Base for future PhishScope suite tools
├── utils/                 # Config, logging, constants, paths
└── logs/                  # Rotating app.log
```

## Tech stack

Python 3.13 · CustomTkinter · ttkbootstrap · requests · cryptography ·
python-whois · dnspython · tldextract · validators · Pillow · SQLite ·
reportlab · PyInstaller

## Contributing

Contributions, issues and feature requests are welcome! Open an issue or send
a PR. Ideas for future modules: port scanner, hash analyzer, DNS/WHOIS
utilities.

## Legal notice

PhishScope is a **defensive** analysis tool. Use it only on URLs you own or
are authorized to review. Data from external services (WHOIS, geolocation,
DNS) is approximate and provider-dependent.

## License

Distributed under the MIT License. See [LICENSE](LICENSE).

---

<details>
<summary><b>Español / Spanish</b></summary>

<div align="center">

# PhishScope

**Análisis defensivo de URLs y detección de phishing — gratuito y offline**

</div>

PhishScope es una aplicación de escritorio para el **análisis defensivo de
URLs**. Evalúa indicadores de phishing y de configuración insegura y los
combina en un **puntaje de riesgo** de 0 a 100, presentado con un medidor
animado y tarjetas de resultado detalladas.

### Características

- **Certificados SSL/TLS**: validez, emisor, versión TLS y días hasta expiración.
- **Información del dominio**: datos WHOIS, antigüedad del registro y registrador.
- **Registros DNS**: consulta A, AAAA, MX, NS y TXT del dominio.
- **IP y geolocalización**: resolución IPv4/IPv6, país, ciudad e ISP.
- **Cadenas de redirección**: número de saltos y URL de destino final.
- **Encabezados de seguridad HTTP**: evaluación de headers clave (HSTS, CSP, etc.).
- **Patrones léxicos de phishing**: heurística sobre la estructura de la URL.
- **Puntaje de riesgo consolidado** (0-100) con medidor animado.
- **Historial persistente** en SQLite con búsqueda y exportación a PDF/JSON/CSV/HTML.
- **Tema oscuro personalizable**.

### Instalación

Descarga `PhishScope.exe` desde la sección
[Releases](https://github.com/Zieragk/PhishScope/releases) (Windows, portable),
o ejecuta desde el código fuente con Python 3.13+:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Aviso legal

Herramienta **defensiva**: analiza únicamente URLs proporcionadas por el
usuario. No incluye funciones ofensivas ni automatiza ataques contra terceros.

</details>
