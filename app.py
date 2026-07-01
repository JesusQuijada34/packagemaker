#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package Maker Web - Flask Application
Uses FlangCompiler from lib/BuildThread.py
"""

import os
import io
import platform
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session
import jwt

from lib.config import Config, config
from lib.auth import create_token
from lib.build import (
    parse_details_xml, build_project, create_project_zip,
    extract_project_from_zip, list_project_files, save_file, project_to_zip
)
from lib.github import get_latest_release, get_release_downloads

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(config.get(os.environ.get('FLASK_ENV', 'default'), Config))
app.secret_key = os.environ.get('SECRET_KEY', 'pm-secret-key-12345')

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# =============================================================================
# PLATFORM DETECTION
# =============================================================================

def detect_client_os(req):
    """Detect client OS from User-Agent header"""
    ua = req.headers.get('User-Agent', '').lower()
    if 'android' in ua:
        return 'android'
    elif 'windows nt 10' in ua or 'windows nt 11' in ua:
        return 'windows11'
    elif 'windows' in ua:
        return 'windows'
    elif 'macintosh' in ua or 'mac os' in ua:
        return 'mac'
    elif 'linux' in ua:
        return 'linux'
    return 'unknown'

def get_recommended_download(downloads, client_os):
    """Get recommended download URL based on client OS"""
    mapping = {
        'windows11': 'windows',
        'windows': 'windows',
        'linux': 'linux',
        'android': None,
        'mac': None
    }
    target = mapping.get(client_os)
    if target:
        return downloads.get(target)
    return None

# =============================================================================
# MICA STYLES - Full Windows 11 / UWP
# =============================================================================

MICA_CSS = """
:root {
    --mica-opacity: 0.75;
    --bg-primary: rgba(32, 32, 32, var(--mica-opacity));
    --bg-secondary: rgba(45, 45, 45, var(--mica-opacity));
    --bg-tertiary: rgba(56, 56, 56, 0.9);
    --bg-hover: rgba(255, 255, 255, 0.05);
    --bg-active: rgba(255, 255, 255, 0.08);
    --text-primary: #ffffff;
    --text-secondary: #cccccc;
    --text-tertiary: #888888;
    --accent: #ff5722;
    --accent-hover: #ff7043;
    --accent-light: rgba(255, 87, 34, 0.15);
    --border-color: rgba(255, 255, 255, 0.06);
    --border-radius: 8px;
    --border-radius-lg: 12px;
    --shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    --blur: blur(100px) saturate(180%);
    --font: 'Segoe UI Variable', 'Segoe UI', system-ui, sans-serif;
    --font-mono: 'Cascadia Code', 'Consolas', monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { height: 100%; font-family: var(--font); font-size: 14px; color: var(--text-primary); background: transparent; overflow: hidden; }

/* Mica Background */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
    z-index: -2;
}
body::after {
    content: '';
    position: fixed;
    inset: 0;
    background: var(--blur);
    z-index: -1;
    opacity: 0.5;
}

/* Mica Effects */
.mica { backdrop-filter: var(--blur); -webkit-backdrop-filter: var(--blur); }
.glass { backdrop-filter: blur(20px) saturate(150%); -webkit-backdrop-filter: blur(20px) saturate(150%); background: rgba(255,255,255,0.03); }

/* Title Bar */
.title-bar { height: 32px; background: var(--bg-secondary); display: flex; align-items: center; justify-content: space-between; padding: 0 8px; -webkit-app-region: drag; border-bottom: 1px solid var(--border-color); }
.title-bar-title { font-size: 12px; font-weight: 500; color: var(--text-secondary); display: flex; align-items: center; gap: 8px; }
.title-bar-controls { display: flex; -webkit-app-region: no-drag; }
.title-bar-btn { width: 46px; height: 32px; border: none; background: transparent; color: var(--text-primary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.1s; }
.title-bar-btn:hover { background: var(--bg-hover); }
.title-bar-btn.close:hover { background: #c42b1c; color: white; }

/* Layout */
.app-container { display: flex; flex-direction: column; height: 100vh; background: transparent; }
.main-content { display: flex; flex: 1; overflow: hidden; }

/* Sidebar - Mica */
.sidebar { width: 220px; background: var(--bg-secondary); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; overflow: hidden; backdrop-filter: var(--blur); }
.sidebar-header { padding: 16px; border-bottom: 1px solid var(--border-color); }
.sidebar-logo { display: flex; align-items: center; gap: 12px; }
.sidebar-logo img { width: 36px; height: 36px; border-radius: 8px; }
.sidebar-logo-text { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.sidebar-logo-version { font-size: 11px; color: var(--text-tertiary); }
.sidebar-nav { flex: 1; padding: 8px; overflow-y: auto; }
.nav-item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: var(--border-radius); color: var(--text-secondary); cursor: pointer; transition: all 0.15s; margin-bottom: 2px; text-decoration: none; font-size: 13px; font-weight: 500; }
.nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.nav-item.active { background: var(--accent-light); color: var(--accent); border-left: 3px solid var(--accent); margin-left: -3px; padding-left: 15px; }
.sidebar-footer { padding: 12px 16px; border-top: 1px solid var(--border-color); }
.sidebar-desc { font-size: 11px; color: var(--text-tertiary); line-height: 1.4; }

/* Content */
.content-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; background: rgba(255,255,255,0.02); }
.content-header { padding: 24px 32px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary); backdrop-filter: var(--blur); }
.content-title { font-size: 24px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.content-subtitle { font-size: 13px; color: var(--text-secondary); }
.content-body { flex: 1; padding: 32px; overflow-y: auto; }

/* Cards - Mica */
.card { background: var(--bg-secondary); border-radius: var(--border-radius-lg); border: 1px solid var(--border-color); padding: 24px; margin-bottom: 16px; backdrop-filter: var(--blur); transition: all 0.2s; }
.card:hover { border-color: rgba(255,255,255,0.12); box-shadow: var(--shadow); }

/* Buttons */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 10px 20px; border-radius: var(--border-radius); font-family: var(--font); font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.15s; border: 1px solid transparent; text-decoration: none; backdrop-filter: blur(10px); }
.btn-primary { background: var(--accent); color: white; }
.btn-primary:hover { background: var(--accent-hover); transform: translateY(-1px); }
.btn-secondary { background: rgba(255,255,255,0.05); color: var(--text-primary); border-color: var(--border-color); }
.btn-secondary:hover { background: rgba(255,255,255,0.1); }
.btn-lg { padding: 14px 28px; font-size: 15px; }
.btn-sm { padding: 8px 14px; font-size: 12px; }

/* Forms */
.form-group { margin-bottom: 20px; }
.form-label { display: block; font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 8px; }
.form-input { width: 100%; padding: 12px 16px; background: rgba(0,0,0,0.2); border: 1px solid var(--border-color); border-radius: var(--border-radius); color: var(--text-primary); font-family: var(--font); font-size: 14px; transition: all 0.15s; backdrop-filter: blur(10px); }
.form-input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-light); }
.form-input::placeholder { color: var(--text-tertiary); }
.form-select { appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23888' d='M2 4l4 4 4-4'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 16px center; padding-right: 40px; }

/* File Tree */
.file-tree { font-family: var(--font-mono); font-size: 12px; }
.file-tree-item { display: flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 6px; cursor: pointer; color: var(--text-secondary); transition: all 0.1s; }
.file-tree-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.file-tree-item.active { background: var(--accent-light); color: var(--accent); }

/* Code Editor */
.code-editor { width: 100%; height: 100%; background: rgba(30,30,30,0.95); color: #d4d4d4; border: none; padding: 20px; font-family: var(--font-mono); font-size: 13px; line-height: 1.6; resize: none; outline: none; backdrop-filter: blur(20px); }

/* Toast */
.toast-container { position: fixed; bottom: 24px; right: 24px; z-index: 9999; display: flex; flex-direction: column; gap: 8px; }
.toast { padding: 14px 20px; border-radius: var(--border-radius); color: white; font-weight: 500; box-shadow: var(--shadow); animation: slideIn 0.3s ease; backdrop-filter: blur(20px); }
.toast-success { background: rgba(16,124,16,0.95); }
.toast-error { background: rgba(196,43,28,0.95); }
.toast-info { background: rgba(0,120,212,0.95); }
@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

/* Download Page */
.download-page { max-width: 700px; margin: 0 auto; padding: 48px 24px; }
.download-header { text-align: center; margin-bottom: 48px; }
.download-icon { width: 96px; height: 96px; margin-bottom: 24px; }
.download-title { font-size: 36px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; }
.download-version { font-size: 18px; color: var(--text-secondary); }
.download-buttons { display: flex; flex-direction: column; gap: 16px; margin-top: 32px; }
.download-btn { display: flex; align-items: center; justify-content: space-between; padding: 24px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--border-radius-lg); color: var(--text-primary); text-decoration: none; transition: all 0.2s; backdrop-filter: var(--blur); }
.download-btn:hover { background: rgba(255,255,255,0.05); border-color: var(--accent); transform: translateY(-2px); box-shadow: var(--shadow); }
.download-btn-icon { width: 48px; height: 48px; background: var(--accent); border-radius: 12px; display: flex; align-items: center; justify-content: center; }
.download-btn-label { font-size: 16px; font-weight: 600; }
.download-btn-sub { font-size: 12px; color: var(--text-tertiary); margin-top: 4px; }

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* Split Pane */
.split-pane { display: flex; height: 100%; }
.split-left { width: 260px; background: var(--bg-secondary); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; backdrop-filter: var(--blur); }
.split-right { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

/* Status Bar */
.status-bar { height: 28px; background: rgba(0,0,0,0.3); border-top: 1px solid var(--border-color); display: flex; align-items: center; padding: 0 16px; font-size: 11px; color: var(--text-tertiary); backdrop-filter: blur(10px); }
.status-item { padding: 0 12px; }

/* Badges */
.badge { display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; }
.badge-primary { background: var(--accent-light); color: var(--accent); }
.badge-success { background: rgba(16,124,16,0.2); color: #6ccb6c; }
.badge-info { background: rgba(0,120,212,0.2); color: #60aaff; }

/* Spinner */
.spinner { width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Drop Zone */
.drop-zone { border: 2px dashed rgba(255,255,255,0.15); border-radius: var(--border-radius-lg); padding: 48px; text-align: center; transition: all 0.2s; cursor: pointer; background: rgba(255,255,255,0.02); }
.drop-zone:hover { border-color: var(--accent); background: var(--accent-light); }
.drop-zone-text { color: var(--text-secondary); font-size: 16px; margin-top: 16px; }
.drop-zone-hint { color: var(--text-tertiary); font-size: 12px; margin-top: 8px; }

/* README */
.readme-content { background: var(--bg-secondary); border-radius: var(--border-radius-lg); padding: 32px; margin-top: 32px; border: 1px solid var(--border-color); }
.readme-content h2 { font-size: 20px; font-weight: 600; color: var(--text-primary); margin: 24px 0 12px; }
.readme-content p { color: var(--text-secondary); line-height: 1.7; margin-bottom: 16px; }
.readme-content ul { color: var(--text-secondary); margin-left: 20px; margin-bottom: 16px; }
.readme-content li { margin-bottom: 8px; }
"""


@app.context_processor
def inject_styles():
    return dict(base_qss=MICA_CSS)


def get_metadata():
    details_path = os.path.join(REPO_ROOT, 'details.xml')
    if os.path.exists(details_path):
        return parse_details_xml(details_path)
    return {'name': 'Package Maker', 'version': 'v3.2.7', 'publisher': 'Influent', 'author': 'JesusQuijada34', 'description': 'Suite for Influent OS ecosystem', 'year': '2025'}


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    # Get download URLs server-side
    downloads = {'windows': None, 'linux': None, 'version': None}
    try:
        release = get_latest_release('', 'JesusQuijada34/packagemaker')
        if release:
            downloads['version'] = release.get('tag_name', '').replace('v', '')
            for asset in release.get('assets', []):
                name = asset.get('name', '').lower()
                url = asset.get('browser_download_url', '')
                if 'knosthalij' in name or 'windows' in name:
                    downloads['windows'] = url
                elif 'danenone' in name or 'linux' in name:
                    downloads['linux'] = url
    except Exception as e:
        print(f"Error fetching downloads: {e}")
    
    return render_template('index.html', metadata=get_metadata(), downloads=downloads)


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        # Handle both JSON and form data
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
        
        required = ['publisher', 'name', 'title', 'author', 'platform']
        for field in required:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing: {field}'}), 400
        
        # Use default version if not provided
        if not data.get('version'):
            data['version'] = 'v1.0.0'
        
        try:
            zip_bytes = create_project_zip(data)
            return send_file(
                io.BytesIO(zip_bytes),
                mimetype='application/zip',
                as_attachment=True,
                download_name=f"{data['name']}.zip"
            )
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('create.html', metadata=get_metadata())


@app.route('/api/create-and-edit', methods=['POST'])
def create_and_edit():
    data = request.json
    for field in ['publisher', 'name', 'version', 'title', 'author', 'platform']:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Missing: {field}'}), 400
    
    import tempfile
    import hashlib
    project_id = hashlib.md5(str(data['name']).encode()).hexdigest()[:8]
    session['project_' + project_id] = data
    return jsonify({'success': True, 'project_id': project_id})


@app.route('/editor')
def editor():
    return render_template('editor.html', metadata=get_metadata())


@app.route('/api/editor/files', methods=['GET', 'POST'])
def editor_files():
    if request.method == 'POST':
        data = request.json
        session['editor_files'] = data.get('files', [])
        return jsonify({'success': True})
    return jsonify({'files': session.get('editor_files', [])})


@app.route('/api/editor/download')
def editor_download():
    files = session.get('editor_files', [])
    if not files:
        return jsonify({'error': 'No files'}), 400
    
    zip_buffer = io.BytesIO()
    with io.BytesIO() as bio:
        import zipfile
        with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in files:
                zf.writestr(f['path'], f.get('content', ''))
        zip_buffer.write(bio.getvalue())
    zip_buffer.seek(0)
    
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='project.zip')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if file and (file.filename.endswith('.zip') or file.filename.endswith('.iflapp')):
            zip_bytes = file.read()
            session['uploaded_project'] = zip_bytes
            return jsonify({'success': True})
    return render_template('upload.html', metadata=get_metadata())


@app.route('/api/uploaded/files')
def get_uploaded_files():
    zip_bytes = session.get('uploaded_project')
    if not zip_bytes:
        return jsonify({'error': 'No uploaded project'}), 400
    
    import tempfile
    import zipfile
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
        zf.extractall(temp_dir)
    
    files = []
    for root, _, filenames in os.walk(temp_dir):
        for fn in filenames:
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, temp_dir)
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                content = '[Binary]'
            files.append({'path': rel, 'name': os.path.basename(fn), 'content': content})
    
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    
    return jsonify({'files': files})


@app.route('/build')
def build_page():
    return render_template('build.html', metadata=get_metadata())


@app.route('/moonfix')
def moonfix():
    return render_template('moonfix.html', metadata=get_metadata())


@app.route('/download')
def download():
    return render_template('download.html', metadata=get_metadata())


@app.route('/api/release')
def api_release():
    token = app.config.get('GITHUB_TOKEN', '')
    repo = app.config.get('GITHUB_REPO', 'JesusQuijada34/packagemaker')
    try:
        release = get_latest_release(token, repo)
        if release:
            downloads = get_release_downloads(release)
            client_os = detect_client_os(request)
            recommended = get_recommended_download(downloads, client_os)
            return jsonify({
                'version': release.get('tag_name', 'v1.0').replace('v', ''),
                'name': release.get('name', ''),
                'body': release.get('body', ''),
                'downloads': downloads,
                'html_url': release.get('html_url', ''),
                'client_os': client_os,
                'recommended': recommended
            })
        return jsonify({'error': 'No release'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/about')
def about():
    return render_template('about.html', metadata=get_metadata())


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found', code=404), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)