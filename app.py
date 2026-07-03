import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify, request, Response, session, send_from_directory, g
import markdown
import sqlite3
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = 'pm-pwa-secret-2026'

SUPPORTED_LANGUAGES = {
    'es': {'name': 'Español', 'native': 'Español'},
    'en': {'name': 'English', 'native': 'English'},
    'pt': {'name': 'Português', 'native': 'Português'},
}

TRANSLATIONS = {
    'es': {
        'nav_home': 'Inicio',
        'nav_download': 'Descargas',
        'nav_release_notes': 'Notas',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. Creado por JesusQuijada34.',
        'footer_language': 'Idioma',
        'hero_badge': '✨ Nueva Versión v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'Tu IDE Profesional para Python ha evolucionado. Crea, empaqueta y distribuye aplicaciones Python con una experiencia moderna y eficiente inspirada en Windows 11.',
        'hero_download': 'Descargar Ahora',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': 'Interfaz intuitiva y potente',
        'section_interface_subtitle': 'Barra de título personalizada Leviathan-UI con efectos visuales acrílico y mica.',
    },
    'en': {
        'nav_home': 'Home',
        'nav_download': 'Downloads',
        'nav_release_notes': 'Notes',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. Crafted by JesusQuijada34.',
        'footer_language': 'Language',
        'hero_badge': '✨ New Version v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'Your professional Python IDE has evolved. Create, package and distribute Python apps with a modern, efficient experience inspired by Windows 11.',
        'hero_download': 'Download Now',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': 'Intuitive and powerful interface',
        'section_interface_subtitle': 'Custom Leviathan-UI title bar with acrylic and mica visual effects.',
    },
    'pt': {
        'nav_home': 'Início',
        'nav_download': 'Downloads',
        'nav_release_notes': 'Notas',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. Criado por JesusQuijada34.',
        'footer_language': 'Idioma',
        'hero_badge': '✨ Nova Versão v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'Seu IDE profissional para Python evoluiu. Crie, empacote e distribua aplicativos Python com uma experiência moderna e eficiente inspirada no Windows 11.',
        'hero_download': 'Baixar agora',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': 'Interface intuitiva e poderosa',
        'section_interface_subtitle': 'Barra de título personalizada do Leviathan-UI com efeitos visuais de acrílico e mica.',
    },
}


def normalize_language(lang_code: str | None) -> str:
    if not lang_code:
        return 'es'
    code = str(lang_code).strip().lower().replace('_', '-')
    if code.startswith('en'):
        return 'en'
    if code.startswith('pt'):
        return 'pt'
    if code.startswith('es'):
        return 'es'
    return 'es'


def resolve_language(request_obj) -> str:
    requested = (
        request_obj.args.get('lang')
        or session.get('lang')
        or request_obj.cookies.get('lang')
        or request_obj.headers.get('X-Language')
        or request_obj.accept_languages.best_match(list(SUPPORTED_LANGUAGES.keys()))
        or 'es'
    )
    return normalize_language(requested)


@app.before_request
def apply_language():
    lang_code = resolve_language(request)
    session['lang'] = lang_code
    g.lang_code = lang_code
    g.lang_name = SUPPORTED_LANGUAGES[lang_code]['name']
    g.translations = TRANSLATIONS[lang_code]
    g.available_languages = SUPPORTED_LANGUAGES


@app.after_request
def persist_language(response):
    if hasattr(g, 'lang_code'):
        response.set_cookie('lang', g.lang_code, max_age=60 * 60 * 24 * 365, path='/', samesite='Lax')
    return response


@app.context_processor
def inject_language_context():
    return {
        'lang_code': getattr(g, 'lang_code', 'es'),
        'lang_name': getattr(g, 'lang_name', 'Español'),
        'translations': getattr(g, 'translations', TRANSLATIONS['es']),
        'available_languages': getattr(g, 'available_languages', SUPPORTED_LANGUAGES),
    }

# Configuración
GITHUB_REPO = "JesusQuijada34/packagemaker"
XML_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/details.xml"
RELEASE_NOTES_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/RELEASE_NOTES.md"
FAQ_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/FAQ.md"
DB_PATH = 'analytics.db'

# Inicializar Base de Datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  timestamp DATETIME,
                  path TEXT,
                  platform TEXT,
                  ip TEXT,
                  duration INTEGER DEFAULT 0,
                  bounced BOOLEAN DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

@app.before_request
def track_visit():
    if not request.path.startswith('/static') and not request.path.startswith('/admin') and not request.path.startswith('/api/track'):
        if 'session_id' not in session: session['session_id'] = str(uuid.uuid4())
        try:
            ua = request.headers.get('User-Agent', '').lower()
            platform = 'Desktop'
            if 'android' in ua: platform = 'Android'
            elif 'windows' in ua: platform = 'Windows'
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO visits (session_id, timestamp, path, platform, ip) VALUES (?, ?, ?, ?, ?)",
                      (session['session_id'], datetime.now(), request.path, platform, request.remote_addr))
            conn.commit()
            conn.close()
        except Exception as e: print(f"Error tracking: {e}")

@app.route('/api/track/update', methods=['POST'])
def update_track():
    data = request.json
    session_id = session.get('session_id')
    if session_id and data:
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE visits SET duration = ?, bounced = ? WHERE session_id = ? ORDER BY id DESC LIMIT 1",
                      (data.get('duration', 0), 0 if data.get('duration', 0) > 5 else 1, session_id))
            conn.commit()
            conn.close()
        except: pass
    return jsonify({"status": "ok"})

# PWA Assets
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def sw():
    return send_from_directory('static', 'sw.js')

@app.route('/app/<path:filename>')
def app_assets(filename):
    return send_from_directory('app', filename)

@app.route('/assets/<path:filename>')
def site_assets(filename):
    return send_from_directory('assets', filename)

def get_xml_metadata():
    try:
        response = requests.get(XML_URL, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            return {child.tag: child.text for child in root}
    except Exception as e:
        print(f"Error fetching XML: {e}")
    return {"version": "v3.2.7", "name": "Package Maker"}

def get_release_info():
    """Get all releases with their assets for download verification"""
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            releases = response.json()
            all_downloads = []
            for release in releases[:5]:  # Latest 5 releases
                version = release.get("tag_name", "")
                assets = release.get("assets", [])
                for asset in assets:
                    name = asset.get("name", "").lower()
                    # Determine platform from filename
                    if "danenone" in name:
                        platform = "Linux"
                        platform_key = "linux"
                    elif "knosthalij" in name:
                        platform = "Windows"
                        platform_key = "windows"
                    else:
                        platform = "Other"
                        platform_key = "other"
                    
                    url = asset.get("browser_download_url", "")
                    all_downloads.append({
                        "name": asset.get("name"),
                        "url": url,
                        "platform": platform,
                        "platform_key": platform_key,
                        "version": version,
                        "size": f"{asset.get('size', 0) / (1024*1024):.2f} MB"
                    })
            return all_downloads
    except Exception as e:
        print(f"Error fetching releases: {e}")
    return []

def check_iflapp_exists(url):
    """Check if an iflapp file exists at the given URL"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def get_github_releases():
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            version = data.get("tag_name", "")
            assets = data.get("assets", [])
            downloads = []
            for asset in assets:
                name = asset.get("name", "").lower()
                platform = "Linux" if "danenone" in name else "Windows"
                downloads.append({"name": asset.get("name"), "url": asset.get("browser_download_url"), "platform": platform, "size": f"{asset.get('size', 0) / (1024*1024):.2f} MB"})
            return version, downloads
    except Exception as e:
        print(f"Error fetching releases: {e}")
    return "v3.2.7", []

def get_download_for_platform(user_agent):
    """Get download info based on platform detection, checking actual file existence"""
    ua = user_agent.lower()
    all_downloads = get_release_info()
    
    # Detect platform
    if "android" in ua or "mobile" in ua:
        detected_platform = "android"
        iflapp_key = None  # No direct iflapp for Android
    elif "win" in ua or "windows" in ua:
        detected_platform = "windows"
        iflapp_key = "windows"
    elif "linux" in ua or "ubuntu" in ua or "debian" in ua:
        detected_platform = "linux"
        iflapp_key = "linux"
    else:
        detected_platform = "desktop"
        iflapp_key = None
    
    # Find direct download for platform from latest release
    direct_download = None
    for dl in all_downloads:
        if dl["platform_key"] == iflapp_key:
            direct_download = dl
            break
    
    # Check if direct download actually exists
    download_status = "available"
    if direct_download:
        # Verify the file exists
        if not check_iflapp_exists(direct_download["url"]):
            download_status = "unavailable"
            direct_download = None
    
    # Get alternatives if no direct download
    alternatives = []
    for dl in all_downloads[:6]:  # Top 6 most recent
        if dl != direct_download:
            alternatives.append(dl)
    
    return {
        "detected_platform": detected_platform,
        "direct_download": direct_download,
        "download_status": download_status,
        "alternatives": alternatives,
        "all_downloads": all_downloads
    }

@app.route('/')
def index():
    print(f"DEBUG: Accessing index from {request.remote_addr}")
    metadata = get_xml_metadata()
    version, _ = get_github_releases()
    ua = request.headers.get('User-Agent', '').lower()
    return render_template('index.html', metadata=metadata, version=version, is_android='android' in ua)

@app.route('/download')
def download():
    print(f"DEBUG: Accessing download from {request.remote_addr}")
    metadata = get_xml_metadata()
    version = metadata.get("version", "v3.2.7")
    ua = request.headers.get('User-Agent', '')
    
    # Get download info with platform detection and existence check
    download_info = get_download_for_platform(ua)
    
    return render_template(
        'download.html', 
        metadata=metadata, 
        version=version, 
        is_android=download_info["detected_platform"] == "android",
        download_info=download_info
    )

@app.route('/faq')
def faq_page():
    try:
        response = requests.get(FAQ_URL, timeout=5)
        content = response.text if response.status_code == 200 else "# FAQ\nNo se pudo cargar el contenido."
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Preguntas Frecuentes", content=html_content)
    except Exception as e:
        print(f"Error loading FAQ: {e}")
        return render_template('error.html', code=500, message="Error al cargar FAQ"), 500

@app.route('/release-notes')
def notes():
    try:
        response = requests.get(RELEASE_NOTES_URL, timeout=5)
        content = response.text if response.status_code == 200 else "# Release Notes"
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Notas de Versión", content=html_content)
    except Exception as e:
        print(f"Error loading notes: {e}")
        return render_template('error.html', code=500, message="Error al cargar Notas"), 500

@app.route('/issues')
def issues_page():
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=open"
        response = requests.get(api_url, timeout=5)
        issues = response.json() if response.status_code == 200 else []
        
        content = "# Problemas Conocidos y Reportes\n\n"
        if not issues:
            content += "Actualmente no hay problemas abiertos reportados. Si encuentras un error, por favor [infórmalo en GitHub](https://github.com/JesusQuijada34/packagemaker/issues).\n"
        else:
            for issue in issues:
                if not issue.get('pull_request'):
                    content += f"### ⚠️ {issue.get('title')}\n"
                    content += f"- **Estado**: {issue.get('state')}\n"
                    content += f"- **Reportado por**: {issue.get('user', {}).get('login')}\n"
                    content += f"- [Ver en GitHub]({issue.get('html_url')})\n\n"
        
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Issues & Soporte", content=html_content)
    except Exception as e:
        print(f"Error loading issues: {e}")
        return render_template('error.html', code=500, message="Error al cargar Issues"), 500

@app.route('/pwaMode')
def pwa_mode():
    mode = request.args.get('id', 'desktop')
    metadata = get_xml_metadata()
    version, downloads = get_github_releases()
    return render_template('pwa.html', mode=mode, metadata=metadata, version=version, downloads=downloads)

@app.route('/api/download.sh')
def download_sh():
    script = """#!/bin/bash
# Package Maker - Auto Installer
RED='\\033[0;31m'
GREEN='\\033[0;32m'
CYAN='\\033[0;36m'
YELLOW='\\033[1;33m'
NC='\\033[0m'
clear
echo -e "${CYAN}====================================================${NC}"
echo -e "${CYAN}       PACKAGE MAKER - INSTALADOR AUTOMÁTICO        ${NC}"
echo -e "${CYAN}====================================================${NC}"
if [ -d "/data/data/com.termux/files/home" ]; then ENV="termux"; else ENV="linux"; fi
if [ "$ENV" == "termux" ]; then pkg update -y && pkg upgrade -y && pkg install -y git python python-pip libexpat openssl
else sudo apt update -y && sudo apt install -y git python3 python3-pip libexpat1; fi
git clone -b main https://github.com/JesusQuijada34/packagemaker.git
cd packagemaker
pip3 install -r lib/requirements.txt
echo -e "${GREEN}INSTALACIÓN COMPLETADA. Inicia con: python3 packagemaker.py${NC}"
"""
    return Response(script, mimetype='text/x-shellscript')

@app.route('/admin/stats')
def admin_stats():
    print(f"DEBUG: Accessing admin_stats from {request.remote_addr}")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM visits"); total = c.fetchone()[0]
        c.execute("SELECT AVG(duration) FROM visits WHERE duration > 0"); avg_time = c.fetchone()[0] or 0
        c.execute("SELECT platform, COUNT(*) FROM visits GROUP BY platform"); platforms = dict(c.fetchall())
        c.execute("SELECT path, COUNT(*) FROM visits GROUP BY path ORDER BY COUNT(*) DESC LIMIT 5"); paths = c.fetchall()
        c.execute("SELECT (COUNT(CASE WHEN bounced = 1 THEN 1 END) * 100.0 / COUNT(*)) FROM visits"); bounce = c.fetchone()[0] or 0
        c.execute("SELECT timestamp, path, platform, duration, bounced FROM visits ORDER BY id DESC LIMIT 20"); recent = c.fetchall()
        conn.close()
        return render_template('stats.html', total=total, avg_time=round(avg_time, 1), platforms=platforms, paths=paths, bounce=round(bounce, 1), recent=recent)
    except Exception as e:
        print(f"DEBUG ERROR in admin_stats: {e}")
        return render_template('error.html', code=500, message=f"Error en base de datos: {e}"), 500

# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, path=request.path), 404

@app.errorhandler(500)
def internal_error(e):
    message = getattr(e, 'description', 'Error Interno del Servidor')
    return render_template('error.html', code=500, message=message), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403), 403

@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code=400), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
