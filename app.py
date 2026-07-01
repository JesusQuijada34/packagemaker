import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify, request, Response, session
import markdown
import sqlite3
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = 'pm-analytics-secret'

# Configuración
GITHUB_REPO = "JesusQuijada34/packagemaker"
XML_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/details.xml"
RELEASE_NOTES_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/RELEASE_NOTES.md"
FAQ_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/FAQ.md"
DB_PATH = 'analytics.db'
WEBHOOK_URL = os.environ.get('ANALYTICS_WEBHOOK') # Opcional: URL de Discord/Slack

# Inicializar Base de Datos Extendida
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

def check_unusual_traffic():
    if not WEBHOOK_URL: return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Contar visitas en los últimos 5 minutos
        five_mins_ago = datetime.now() - timedelta(minutes=5)
        c.execute("SELECT COUNT(*) FROM visits WHERE timestamp > ?", (five_mins_ago,))
        count = c.fetchone()[0]
        conn.close()
        
        if count > 50: # Umbral de alerta
            requests.post(WEBHOOK_URL, json={
                "content": f"⚠️ **Alerta de Tráfico Inusual**: {count} visitas en los últimos 5 minutos en Package Maker."
            })
    except Exception as e:
        print(f"Error checking traffic: {e}")

@app.before_request
def track_visit():
    if not request.path.startswith('/static') and not request.path.startswith('/admin') and not request.path.startswith('/api/track'):
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        try:
            ua = request.headers.get('User-Agent', '').lower()
            platform = 'Desktop'
            if 'android' in ua: platform = 'Android'
            elif 'windows' in ua: platform = 'Windows'
            elif 'linux' in ua: platform = 'Linux'
            elif 'iphone' in ua or 'ipad' in ua: platform = 'iOS'
            
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO visits (session_id, timestamp, path, platform, ip) VALUES (?, ?, ?, ?, ?)",
                      (session['session_id'], datetime.now(), request.path, platform, request.remote_addr))
            conn.commit()
            conn.close()
            check_unusual_traffic()
        except Exception as e:
            print(f"Error logging visit: {e}")

@app.route('/api/track/update', methods=['POST'])
def update_track():
    data = request.json
    session_id = session.get('session_id')
    if session_id and data:
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            # Si el usuario interactuó o estuvo más de 5s, no es rebote
            duration = data.get('duration', 0)
            bounced = 0 if duration > 5 else 1
            c.execute("UPDATE visits SET duration = ?, bounced = ? WHERE session_id = ? ORDER BY timestamp DESC LIMIT 1",
                      (duration, bounced, session_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating track: {e}")
    return jsonify({"status": "ok"})

# Rutas de Información
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
                if "danenone" in name.lower(): platform = "Linux (Danenone)"
                elif "knosthalij" in name.lower(): platform = "Windows (Knosthalij)"
                downloads.append({"name": name, "url": url, "platform": platform, "size": f"{asset.get('size', 0) / (1024*1024):.2f} MB"})
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
    except Exception as e: return str(e)

@app.route('/admin/stats')
def stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM visits")
    total_visits = c.fetchone()[0]
    
    c.execute("SELECT AVG(duration) FROM visits WHERE duration > 0")
    avg_duration = c.fetchone()[0] or 0
    
    c.execute("SELECT (CAST(SUM(bounced) AS FLOAT) / COUNT(*)) * 100 FROM visits")
    bounce_rate = c.fetchone()[0] or 0
    
    c.execute("SELECT platform, COUNT(*) FROM visits GROUP BY platform")
    platform_stats = dict(c.fetchall())
    
    c.execute("SELECT path, COUNT(*) FROM visits GROUP BY path ORDER BY COUNT(*) DESC LIMIT 5")
    path_stats = c.fetchall()
    
    c.execute("SELECT timestamp, path, platform, duration, bounced FROM visits ORDER BY timestamp DESC LIMIT 15")
    recent_visits = c.fetchall()
    
    conn.close()
    return render_template('stats.html', total=total_visits, avg_time=round(avg_duration, 2), bounce=round(bounce_rate, 2), platforms=platform_stats, paths=path_stats, recent=recent_visits)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
