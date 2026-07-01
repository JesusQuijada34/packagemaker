import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify, request
import markdown

app = Flask(__name__)

# Configuración
GITHUB_REPO = "JesusQuijada34/packagemaker"
XML_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/details.xml"
RELEASE_NOTES_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/RELEASE_NOTES.md"
FAQ_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/FAQ.md"

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
        # Usamos la API de GitHub para obtener los assets del último release
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
                # Lógica de plataforma basada en el nombre del archivo iflapp
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
    version, downloads = get_github_releases()
    return render_template('index.html', metadata=metadata, version=version, downloads=downloads)

@app.route('/release-notes')
def release_notes():
    try:
        response = requests.get(RELEASE_NOTES_URL)
        content = response.text if response.status_code == 200 else "No se pudieron cargar las notas de versión."
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Notas de Versión", content=html_content)
    except Exception as e:
        return str(e)

@app.route('/faq')
def faq():
    try:
        response = requests.get(FAQ_URL)
        content = response.text if response.status_code == 200 else "No se pudo cargar el FAQ."
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Preguntas Frecuentes", content=html_content)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
