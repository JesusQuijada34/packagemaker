import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify, request, Response, session, send_from_directory
import markdown
import sqlite3
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = 'pm-pwa-secret-2026'

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

def get_xml_metadata():
    try:
        response = requests.get(XML_URL)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            return {child.tag: child.text for child in root}
    except: pass
    return {"version": "v3.2.7", "name": "Package Maker"}

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
                name = asset.get("name", "").lower()
                platform = "Linux" if "danenone" in name else "Windows"
                downloads.append({"name": asset.get("name"), "url": asset.get("browser_download_url"), "platform": platform, "size": f"{asset.get('size', 0) / (1024*1024):.2f} MB"})
            return version, downloads
    except: pass
    return "v3.2.7", []

@app.route('/')
def index():
    metadata = get_xml_metadata()
    version, _ = get_github_releases()
    ua = request.headers.get('User-Agent', '').lower()
    return render_template('index.html', metadata=metadata, version=version, is_android='android' in ua)

@app.route('/download')
def download():
    metadata = get_xml_metadata()
    version, downloads = get_github_releases()
    ua = request.headers.get('User-Agent', '').lower()
    return render_template('download.html', metadata=metadata, version=version, downloads=downloads, is_android='android' in ua)

@app.route('/faq')
def faq_page():
    try:
        response = requests.get(FAQ_URL)
        content = response.text if response.status_code == 200 else "# FAQ\nNo se pudo cargar el contenido."
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Preguntas Frecuentes", content=html_content)
    except: return "Error al cargar FAQ"

@app.route('/release-notes')
def notes():
    try:
        response = requests.get(RELEASE_NOTES_URL)
        content = response.text if response.status_code == 200 else "# Release Notes"
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Notas de Versión", content=html_content)
    except: return "Error al cargar Notas"

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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM visits"); total = c.fetchone()[0]
    c.execute("SELECT AVG(duration) FROM visits WHERE duration > 0"); avg_time = c.fetchone()[0] or 0
    c.execute("SELECT platform, COUNT(*) FROM visits GROUP BY platform"); platforms = dict(c.fetchall())
    c.execute("SELECT timestamp, path, platform, duration FROM visits ORDER BY id DESC LIMIT 20"); recent = c.fetchall()
    conn.close()
    return render_template('stats.html', total=total, avg_time=round(avg_time, 1), platforms=platforms, recent=recent)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
