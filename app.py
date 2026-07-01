import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify, request, Response
import markdown
import sqlite3
from datetime import datetime

app = Flask(__name__)

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
                  timestamp DATETIME,
                  path TEXT,
                  platform TEXT,
                  user_agent TEXT,
                  ip TEXT)''')
    conn.commit()
    conn.close()

init_db()

def log_visit():
    try:
        ua = request.headers.get('User-Agent', '').lower()
        platform = 'Desconocida'
        if 'android' in ua: platform = 'Android'
        elif 'windows' in ua: platform = 'Windows'
        elif 'linux' in ua: platform = 'Linux'
        elif 'iphone' in ua or 'ipad' in ua: platform = 'iOS'
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO visits (timestamp, path, platform, user_agent, ip) VALUES (?, ?, ?, ?, ?)",
                  (datetime.now(), request.path, platform, ua, request.remote_addr))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging visit: {e}")

@app.before_request
def before_request():
    if not request.path.startswith('/static') and not request.path.startswith('/admin'):
        log_visit()

def get_xml_metadata():
    try:
        response = requests.get(XML_URL)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            metadata = {child.tag: child.text for child in root}
            return metadata
    except Exception as e:
        print(f"Error fetching XML: {e}")
    return {"version": "Desconocida", "name": "Package Maker"}

def get_github_releases():
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            version = data.get("tag_name", "")
            assets = data.get("assets", [])
            downloads = []
            for asset in assets:
                name = asset.get("name", "")
                url = asset.get("browser_download_url", "")
                platform = "Desconocida"
                if "danenone" in name.lower():
                    platform = "Linux (Danenone)"
                elif "knosthalij" in name.lower():
                    platform = "Windows (Knosthalij)"
                
                downloads.append({
                    "name": name,
                    "url": url,
                    "platform": platform,
                    "size": f"{asset.get('size', 0) / (1024*1024):.2f} MB"
                })
            return version, downloads
    except Exception as e:
        print(f"Error fetching releases: {e}")
    return None, []

@app.route('/')
def index():
    metadata = get_xml_metadata()
    version, _ = get_github_releases()
    ua = request.headers.get('User-Agent', '').lower()
    is_android = 'android' in ua
    return render_template('index.html', metadata=metadata, version=version, is_android=is_android)

@app.route('/download')
def download():
    metadata = get_xml_metadata()
    version, downloads = get_github_releases()
    ua = request.headers.get('User-Agent', '').lower()
    is_android = 'android' in ua
    return render_template('download.html', metadata=metadata, version=version, downloads=downloads, is_android=is_android)

@app.route('/release-notes')
def release_notes():
    try:
        response = requests.get(RELEASE_NOTES_URL)
        content = response.text if response.status_code == 200 else "No se pudieron cargar las notas de versión."
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Notas de Versión", content=html_content)
    except Exception as e:
        return str(e)

@app.route('/admin/stats')
def stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Total visitas
    c.execute("SELECT COUNT(*) FROM visits")
    total_visits = c.fetchone()[0]
    
    # Visitas por plataforma
    c.execute("SELECT platform, COUNT(*) FROM visits GROUP BY platform")
    platform_stats = dict(c.fetchall())
    
    # Visitas por ruta
    c.execute("SELECT path, COUNT(*) FROM visits GROUP BY path ORDER BY COUNT(*) DESC LIMIT 5")
    path_stats = c.fetchall()
    
    # Últimas 10 visitas
    c.execute("SELECT timestamp, path, platform, ip FROM visits ORDER BY timestamp DESC LIMIT 10")
    recent_visits = c.fetchall()
    
    conn.close()
    return render_template('stats.html', total=total_visits, platforms=platform_stats, paths=path_stats, recent=recent_visits)

@app.route('/api/download.sh')
def download_sh():
    script = """#!/bin/bash
# Package Maker - Auto Installer for Termux/Linux
# Creado por Influent (JesusQuijada34)

RED='\\033[0;31m'
GREEN='\\033[0;32m'
CYAN='\\033[0;36m'
YELLOW='\\033[1;33m'
NC='\\033[0m'

clear
echo -e "${CYAN}====================================================${NC}"
echo -e "${CYAN}       PACKAGE MAKER - INSTALADOR AUTOMÁTICO        ${NC}"
echo -e "${CYAN}====================================================${NC}"

if [ -d "/data/data/com.termux/files/home" ]; then
    ENV="termux"
    echo -e "${GREEN}[+] Entorno Termux detectado.${NC}"
else
    ENV="linux"
    echo -e "${GREEN}[+] Entorno Linux detectado.${NC}"
fi

echo -e "${YELLOW}[*] Instalando dependencias del sistema...${NC}"
if [ "$ENV" == "termux" ]; then
    pkg update -y && pkg upgrade -y
    pkg install -y git python python-pip libexpat openssl
else
    sudo apt update -y
    sudo apt install -y git python3 python3-pip libexpat1
fi

echo -e "${YELLOW}[*] Clonando repositorio (rama main)...${NC}"
rm -rf packagemaker
git clone -b main https://github.com/JesusQuijada34/packagemaker.git
cd packagemaker

echo -e "${YELLOW}[*] Instalando requerimientos desde lib/requirements.txt...${NC}"
if [ "$ENV" == "termux" ]; then
    pip install -r lib/requirements.txt
else
    pip3 install -r lib/requirements.txt
fi

echo -e "${CYAN}====================================================${NC}"
echo -e "${GREEN}      INSTALACIÓN COMPLETADA CON ÉXITO             ${NC}"
echo -e "${CYAN}====================================================${NC}"
echo -e "${WHITE}Inicia con:${NC} ${YELLOW}python3 packagemaker.py${NC}"
"""
    return Response(script, mimetype='text/x-shellscript')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
