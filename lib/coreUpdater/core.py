#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core utilities and logic for the updater system.
"""
import sys
import os
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime

# requests con fallback a urllib
try:
    import requests
except ImportError:
    requests = None

# --- CONFIG ---
XML_PATH = "details.xml"
LOG_PATH = "updater_log.txt"
CHECK_INTERVAL = 60
GITHUB_API = "https://api.github.com"

# --- CACHE EN MEMORIA ---
_memory_cache = {}

def log(msg):
    ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except: pass
    print(f"{ts} {msg}")

def _rXml(path):
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        return {
            "app": root.findtext("app", "").strip(),
            "version": root.findtext("version", "").strip(),
            "platform": root.findtext("platform", "").strip(),
            "author": root.findtext("author", "").strip(),
            "publisher": root.findtext("publisher", "").strip()
        }
    except: return {}

def _rXml_r(author, app):
    url = f"https://raw.githubusercontent.com/{author}/{app}/main/details.xml"
    try:
        if requests:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return ET.fromstring(r.text).findtext("version", "").strip()
        else:
            # Fallback usando urllib
            import urllib.request
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    content = response.read().decode('utf-8')
                    return ET.fromstring(content).findtext("version", "").strip()
    except: pass
    return ""

def _check_url_exists(url):
    """Verifica si una URL existe (HEAD request)."""
    if requests:
        try:
            r = requests.head(url, timeout=15, allow_redirects=True)
            return r.status_code == 200
        except: pass
    else:
        # Fallback usando urllib
        try:
            import urllib.request
            req = urllib.request.Request(url, method='HEAD')
            with urllib.request.urlopen(req, timeout=15) as response:
                return response.status == 200
        except: pass
    return False

def _fR(author, app, version, platform, publisher):
    filename = f"{publisher}.{app}.{version}-{platform}.iflapp"
    url = f"https://github.com/{author}/{app}/releases/download/{version}/{filename}"
    if _check_url_exists(url):
        return url
    return None

def _fR_exe(author, app, version, platform, publisher):
    """Busca ejecutable setup con formato: Publisher.App-Version-Platform.exe"""
    # Formato largo de packagemaker: Publisher.App-Version-Platform.exe
    exe_patterns = [
        f"{publisher}.{app}-{version}-{platform}.exe",
        f"{publisher}.{app}.{version}-{platform}.exe",
        f"{publisher}-{app}-{version}-{platform}.exe",
        f"{app}-{version}-{platform}.exe",
        f"{publisher}.{app}-Setup-{version}.exe",
        f"{app}-Setup-{version}.exe",
        f"{publisher}.{app}-{version}.exe",
    ]
    
    for filename in exe_patterns:
        url = f"https://github.com/{author}/{app}/releases/download/{version}/{filename}"
        if _check_url_exists(url):
            log(f"[EXE] Setup encontrado: {filename}")
            return url, filename
    
    return None, None

def cache_get(key):
    """Obtiene valor de caché en memoria."""
    return _memory_cache.get(key)

def cache_set(key, value):
    """Guarda valor en caché en memoria."""
    _memory_cache[key] = value

def cache_clear():
    """Limpia caché en memoria."""
    _memory_cache.clear()

class KillerLogic:
    @staticmethod
    def kill_target(target_name):
        log(f"Matando procesos de: {target_name}")
        try:
            if sys.platform == "win32":
                subprocess.call(f"taskkill /F /IM {target_name}.exe", shell=True)
                subprocess.call(f"taskkill /F /IM {target_name}", shell=True) 
            else:
                subprocess.call(f"pkill -9 -f {target_name}", shell=True)
        except Exception as e:
            log(f"Kill error: {e}")
