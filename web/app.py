#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package Maker Web - Flask Application
Influent Package Maker - Web Interface
"""

import os
import sys
import io
import zipfile
import json
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, jsonify, send_file,
    redirect, url_for, Response
)
import jwt

# Import local modules
from lib.config import Config, config
from lib.auth import create_token, verify_token, api_login_required
from lib.build import (
    parse_details_xml, extract_project_from_zip, build_project,
    create_project_structure, package_to_zip
)
from lib.github import (
    get_latest_release, get_release_downloads, upload_release_asset,
    create_release, get_release_notes_content
)

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(config.get(os.environ.get('FLASK_ENV', 'default'), Config))

# Get repo root for accessing details.xml
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# =============================================================================
# QSS STYLES - Windows 11 / UWP Inspired
# =============================================================================

BASE_QSS = """
:root {
    --bg-primary: #202020;
    --bg-secondary: #2d2d2d;
    --bg-tertiary: #383838;
    --bg-hover: rgba(255, 255, 255, 0.05);
    --bg-active: rgba(255, 255, 255, 0.08);
    --text-primary: #ffffff;
    --text-secondary: #b0b0b0;
    --text-tertiary: #808080;
    --accent: #ff5722;
    --accent-hover: #ff7043;
    --accent-light: rgba(255, 87, 34, 0.2);
    --border-color: rgba(255, 255, 255, 0.08);
    --border-radius: 8px;
    --border-radius-lg: 12px;
    --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.2);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.4);
    --mica-blur: blur(20px);
    --font-family: 'Segoe UI Variable', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'Cascadia Code', 'Consolas', monospace;
}

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { height: 100%; font-family: var(--font-family); font-size: 14px; color: var(--text-primary); background: var(--bg-primary); overflow: hidden; }

.mica { background: rgba(32, 32, 32, 0.85); backdrop-filter: var(--mica-blur); -webkit-backdrop-filter: var(--mica-blur); }

/* Title Bar */
.title-bar { height: 32px; background: var(--bg-secondary); display: flex; align-items: center; justify-content: space-between; padding: 0 8px; -webkit-app-region: drag; }
.title-bar-title { font-size: 12px; font-weight: 600; color: var(--text-secondary); display: flex; align-items: center; gap: 8px; }
.title-bar-controls { display: flex; -webkit-app-region: no-drag; }
.title-bar-btn { width: 46px; height: 32px; border: none; background: transparent; color: var(--text-primary); cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.1s; }
.title-bar-btn:hover { background: var(--bg-hover); }
.title-bar-btn.close:hover { background: #c42b1c; color: white; }
.title-bar-btn svg { width: 16px; height: 16px; }

/* Layout */
.app-container { display: flex; flex-direction: column; height: 100vh; background: var(--bg-primary); }
.main-content { display: flex; flex: 1; overflow: hidden; }

/* Sidebar */
.sidebar { width: 240px; min-width: 240px; background: var(--bg-secondary); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; overflow-y: auto; }
.sidebar-header { padding: 16px; border-bottom: 1px solid var(--border-color); }
.sidebar-logo { display: flex; align-items: center; gap: 12px; }
.sidebar-logo img { width: 32px; height: 32px; border-radius: 6px; }
.sidebar-logo-text { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.sidebar-logo-version { font-size: 11px; color: var(--text-tertiary); }
.sidebar-nav { flex: 1; padding: 8px; }
.nav-item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: var(--border-radius); color: var(--text-secondary); cursor: pointer; transition: all 0.15s ease; margin-bottom: 2px; text-decoration: none; }
.nav-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.nav-item.active { background: var(--accent-light); color: var(--accent); border-left: 3px solid var(--accent); margin-left: -3px; }
.nav-item-icon { width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; }
.sidebar-footer { padding: 12px 16px; border-top: 1px solid var(--border-color); }
.sidebar-desc { font-size: 12px; color: var(--text-tertiary); line-height: 1.5; }

/* Content */
.content-area { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.content-header { padding: 20px 24px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary); }
.content-title { font-size: 28px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.content-subtitle { font-size: 14px; color: var(--text-secondary); }
.content-body { flex: 1; padding: 24px; overflow-y: auto; }

/* Cards */
.card { background: var(--bg-secondary); border-radius: var(--border-radius-lg); border: 1px solid var(--border-color); padding: 20px; margin-bottom: 16px; transition: all 0.2s ease; }
.card:hover { border-color: rgba(255, 255, 255, 0.15); box-shadow: var(--shadow-md); }
.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.card-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }

/* Buttons */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 8px 16px; border-radius: var(--border-radius); font-family: var(--font-family); font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.15s ease; border: 1px solid transparent; text-decoration: none; }
.btn-primary { background: var(--accent); color: white; border-color: var(--accent); }
.btn-primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); }
.btn-secondary { background: transparent; color: var(--text-primary); border-color: var(--border-color); }
.btn-secondary:hover { background: var(--bg-hover); border-color: rgba(255, 255, 255, 0.15); }
.btn-lg { padding: 12px 24px; font-size: 15px; }
.btn-sm { padding: 6px 12px; font-size: 12px; }

/* Forms */
.form-group { margin-bottom: 16px; }
.form-label { display: block; font-size: 14px; font-weight: 500; color: var(--text-secondary); margin-bottom: 6px; }
.form-input { width: 100%; padding: 10px 14px; background: var(--bg-tertiary); border: 1px solid var(--border-color); border-radius: var(--border-radius); color: var(--text-primary); font-family: var(--font-family); font-size: 14px; transition: all 0.15s ease; }
.form-input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent-light); }
.form-input::placeholder { color: var(--text-tertiary); }
.form-select { appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23808080' d='M2 4l4 4 4-4'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 12px center; padding-right: 36px; }
.form-textarea { min-height: 100px; resize: vertical; }

/* Progress */
.progress { height: 4px; background: var(--bg-tertiary); border-radius: 2px; overflow: hidden; }
.progress-bar { height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.3s ease; }

/* File Tree */
.file-tree { font-family: var(--font-mono); font-size: 13px; }
.file-tree-item { display: flex; align-items: center; gap: 6px; padding: 4px 8px; border-radius: 4px; cursor: pointer; color: var(--text-secondary); }
.file-tree-item:hover { background: var(--bg-hover); color: var(--text-primary); }
.file-tree-item.active { background: var(--accent-light); color: var(--accent); }

/* Code Editor */
.code-editor { width: 100%; height: 100%; background: #1e1e1e; color: #d4d4d4; border: none; padding: 16px; font-family: var(--font-mono); font-size: 13px; line-height: 1.5; resize: none; outline: none; }

/* Toast */
.toast-container { position: fixed; bottom: 24px; right: 24px; z-index: 2000; display: flex; flex-direction: column; gap: 8px; }
.toast { padding: 14px 20px; border-radius: var(--border-radius); color: white; font-weight: 500; box-shadow: var(--shadow-md); animation: slideIn 0.3s ease; }
.toast-success { background: #107c10; }
.toast-error { background: #c42b1c; }
.toast-info { background: #0078d4; }
@keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

/* Download Page */
.download-page { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
.download-header { text-align: center; margin-bottom: 40px; }
.download-icon { width: 80px; height: 80px; margin-bottom: 20px; }
.download-title { font-size: 32px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px; }
.download-version { font-size: 16px; color: var(--text-secondary); }
.download-buttons { display: flex; flex-direction: column; gap: 16px; margin-top: 32px; }
.download-btn { display: flex; align-items: center; justify-content: space-between; padding: 20px 24px; background: var(--bg-secondary); border: 1px solid var(--border-color); border-radius: var(--border-radius-lg); color: var(--text-primary); text-decoration: none; transition: all 0.2s ease; }
.download-btn:hover { background: var(--bg-tertiary); border-color: var(--accent); }
.download-btn-text { display: flex; align-items: center; gap: 16px; }
.download-btn-icon { width: 40px; height: 40px; background: var(--accent); border-radius: 8px; display: flex; align-items: center; justify-content: center; }
.download-btn-label { font-size: 16px; font-weight: 600; }
.download-btn-sub { font-size: 12px; color: var(--text-tertiary); }
.download-btn-arrow { color: var(--text-tertiary); }

/* README */
.readme-content { background: var(--bg-secondary); border-radius: var(--border-radius-lg); padding: 32px; margin-top: 32px; }
.readme-content h1 { font-size: 28px; font-weight: 600; color: var(--text-primary); margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border-color); }
.readme-content h2 { font-size: 22px; font-weight: 600; color: var(--text-primary); margin: 24px 0 12px; }
.readme-content p { color: var(--text-secondary); line-height: 1.7; margin-bottom: 16px; }
.readme-content code { background: var(--bg-tertiary); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 13px; color: #ce9178; }
.readme-content ul, .readme-content ol { color: var(--text-secondary); margin-left: 24px; margin-bottom: 16px; }
.readme-content li { margin-bottom: 8px; }
.readme-content a { color: var(--accent); text-decoration: none; }

/* Scrollbar */
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--bg-tertiary); border-radius: 5px; border: 2px solid var(--bg-primary); }

/* Split Pane */
.split-pane { display: flex; height: 100%; }
.split-left { width: 280px; min-width: 200px; background: var(--bg-secondary); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; }
.split-right { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

/* Status Bar */
.status-bar { height: 24px; background: var(--bg-tertiary); border-top: 1px solid var(--border-color); display: flex; align-items: center; padding: 0 12px; font-size: 12px; color: var(--text-tertiary); }
.status-item { padding: 0 8px; }

/* Badges */
.badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; }
.badge-primary { background: var(--accent-light); color: var(--accent); }
.badge-success { background: rgba(16, 124, 16, 0.2); color: #6ccb6c; }
.badge-info { background: rgba(0, 120, 212, 0.2); color: #60aaff; }

/* Spinner */
.spinner { width: 40px; height: 40px; border: 3px solid var(--bg-tertiary); border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Drop Zone */
.drop-zone { border: 2px dashed var(--border-color); border-radius: var(--border-radius-lg); padding: 40px; text-align: center; transition: all 0.2s ease; cursor: pointer; }
.drop-zone:hover, .drop-zone.dragover { border-color: var(--accent); background: var(--accent-light); }
.drop-zone-icon { font-size: 48px; color: var(--text-tertiary); margin-bottom: 16px; }
.drop-zone-text { color: var(--text-secondary); font-size: 16px; }
.drop-zone-hint { color: var(--text-tertiary); font-size: 12px; margin-top: 8px; }
"""


@app.context_processor
def inject_styles():
    return dict(base_qss=BASE_QSS)


def get_metadata():
    """Get app metadata from details.xml"""
    details_path = os.path.join(REPO_ROOT, 'details.xml')
    if os.path.exists(details_path):
        return parse_details_xml(details_path)
    return {
        'name': 'Package Maker',
        'version': 'v3.2.7',
        'publisher': 'Influent',
        'author': 'JesusQuijada34'
    }


# =============================================================================
# ROUTES
# =============================================================================

@app.route('/')
def index():
    metadata = get_metadata()
    return render_template('index.html', metadata=metadata)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username and password:
        token = create_token({'username': username}, app.config['JWT_SECRET'])
        response = jsonify({'success': True, 'token': token})
        response.set_cookie('auth_token', token, httponly=True, samesite='Lax')
        return response
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401


@app.route('/create')
def create():
    metadata = get_metadata()
    return render_template('create.html', metadata=metadata)


@app.route('/api/create-project', methods=['POST'])
def api_create_project():
    data = request.json
    required = ['publisher', 'name', 'version', 'title', 'author', 'platform']
    for field in required:
        if not data.get(field):
            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
    
    try:
        project_path = create_project_structure(
            app.config['PROJECTS_FOLDER'], data
        )
        return jsonify({'success': True, 'project_name': data['name']})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/editor/<project_name>')
def editor(project_name):
    project_path = os.path.join(app.config['PROJECTS_FOLDER'], project_name)
    if not os.path.exists(project_path):
        return "Project not found", 404
    
    files = []
    for root, dirs, filenames in os.walk(project_path):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, project_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                content = '[Binary file]'
            files.append({'path': rel_path, 'name': filename, 'content': content})
    
    metadata = get_metadata()
    return render_template('editor.html', project_name=project_name, files=files, metadata=metadata)


@app.route('/api/project/<project_name>/files')
def get_project_files(project_name):
    project_path = os.path.join(app.config['PROJECTS_FOLDER'], project_name)
    if not os.path.exists(project_path):
        return jsonify({'error': 'Project not found'}), 404
    
    files = []
    for root, dirs, filenames in os.walk(project_path):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, project_path)
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                content = '[Binary file]'
            files.append({'path': rel_path, 'name': filename, 'content': content})
    
    return jsonify({'files': files})


@app.route('/api/project/<project_name>/save', methods=['POST'])
def save_project_file(project_name):
    project_path = os.path.join(app.config['PROJECTS_FOLDER'], project_name)
    if not os.path.exists(project_path):
        return jsonify({'error': 'Project not found'}), 404
    
    data = request.json
    if '..' in data['path'] or data['path'].startswith('/'):
        return jsonify({'error': 'Invalid path'}), 400
    
    try:
        file_path = os.path.join(project_path, data['path'])
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/<project_name>/download')
def download_project(project_name):
    project_path = os.path.join(app.config['PROJECTS_FOLDER'], project_name)
    if not os.path.exists(project_path):
        return "Project not found", 404
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_path)
                zipf.write(file_path, arcname)
    
    memory_file.seek(0)
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name=f'{project_name}.zip')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and (file.filename.endswith('.zip') or file.filename.endswith('.iflapp')):
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(upload_path)
            
            project_name = os.path.splitext(file.filename)[0]
            extract_path = os.path.join(app.config['PROJECTS_FOLDER'], project_name)
            
            try:
                extract_project_from_zip(upload_path, extract_path)
                return redirect(url_for('editor', project_name=project_name))
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    metadata = get_metadata()
    return render_template('upload.html', metadata=metadata)


@app.route('/build')
def build():
    projects = []
    for item in os.listdir(app.config['PROJECTS_FOLDER']):
        item_path = os.path.join(app.config['PROJECTS_FOLDER'], item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'details.xml')):
            metadata = parse_details_xml(os.path.join(item_path, 'details.xml'))
            projects.append({'name': item, 'metadata': metadata})
    
    app_metadata = get_metadata()
    return render_template('build.html', projects=projects, metadata=app_metadata)


@app.route('/api/build/<project_name>', methods=['POST'])
def api_build_project(project_name):
    project_path = os.path.join(app.config['PROJECTS_FOLDER'], project_name)
    if not os.path.exists(project_path):
        return jsonify({'error': 'Project not found'}), 404
    
    target = request.json.get('target', 'Linux')
    
    try:
        result = build_project(project_path, target)
        if result:
            return jsonify({'success': True, 'output': result})
        else:
            return jsonify({'success': False, 'error': 'Build failed. Check logs.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download')
def download():
    metadata = get_metadata()
    return render_template('download.html', metadata=metadata)


@app.route('/api/github-release')
def api_github_release():
    token = app.config.get('GITHUB_TOKEN')
    repo = app.config.get('GITHUB_REPO')
    
    if not token:
        return jsonify({'error': 'GitHub token not configured'}), 500
    
    try:
        release = get_latest_release(token, repo)
        if release:
            downloads = get_release_downloads(release)
            version = release.get('tag_name', 'v1.0').replace('v', '')
            return jsonify({
                'version': version,
                'tag': release.get('tag_name'),
                'name': release.get('name'),
                'body': release.get('body'),
                'downloads': downloads,
                'html_url': release.get('html_url')
            })
        return jsonify({'error': 'Release not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/moonfix')
def moonfix():
    metadata = get_metadata()
    return render_template('moonfix.html', metadata=metadata)


@app.route('/about')
def about():
    metadata = get_metadata()
    return render_template('about.html', metadata=metadata)


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found', code=404), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Server error', code=500), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)