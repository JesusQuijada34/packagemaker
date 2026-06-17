# -*- coding: utf-8 -*-
import os
import io
import zipfile
import hashlib
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime

def parse_details_xml(xml_path):
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        return {
            'publisher': root.findtext('publisher') or 'Unknown',
            'app': root.findtext('app') or 'Unknown',
            'name': root.findtext('name') or 'Unknown',
            'version': root.findtext('version') or 'v1.0',
            'platform': root.findtext('platform') or 'AlphaCube',
            'author': root.findtext('author') or 'Unknown',
            'description': root.findtext('description') or '',
            'rate': root.findtext('rate') or 'All ages',
            'year': root.findtext('year') or datetime.now().year
        }
    except:
        return {'publisher': 'Unknown', 'app': 'Unknown', 'name': 'Unknown', 'version': 'v1.0', 'platform': 'AlphaCube', 'author': 'Unknown', 'description': '', 'rate': 'All ages', 'year': datetime.now().year}

def build_project(project_path, target_platform='Linux', log_callback=None):
    def log(msg):
        if log_callback: log_callback(msg)
        else: print(f"[BUILD] {msg}")
    try:
        from lib.BuildThread import FlangCompiler
        from pathlib import Path
        output_path = Path(tempfile.mkdtemp(prefix='pm_build_'))
        compiler = FlangCompiler(repo_path=Path(project_path), output_path=output_path, log_callback=log)
        result = compiler.run(build_mode="portable")
        return str(result) if result else None
    except ImportError as e:
        log(f"[ERROR] Could not import FlangCompiler: {e}")
        return None
    except Exception as e:
        log(f"[ERROR] Build failed: {e}")
        return None

def create_project_zip(project_data):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        main_script = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{project_data['name']} - {project_data['title']}
Version: {project_data['version']}
Author: {project_data['author']}
"""
def main():
    print("Hello from {project_data['name']}!")
if __name__ == "__main__":
    main()
'''
        zf.writestr(f"{project_data['app']}.py", main_script)
        details_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<app>
    <publisher>{project_data['publisher']}</publisher>
    <app>{project_data['app']}</app>
    <name>{project_data['title']}</name>
    <version>{project_data['version']}</version>
    <correlationid>{hashlib.md5(str(datetime.now()).encode()).hexdigest()}</correlationid>
    <rate>Todas las edades</rate>
    <author>{project_data['author']}</author>
    <platform>{project_data['platform']}</platform>
    <description>{project_data.get('description', '')}</description>
    <year>{datetime.now().year}</year>
</app>
'''
        zf.writestr('details.xml', details_xml)
        readme = f'''# {project_data['title']}
{project_data.get('description', 'A Fluthin application')}
## Information
- Publisher: {project_data['publisher']}
- Author: {project_data['author']}
- Version: {project_data['version']}
- Platform: {project_data['platform']}
'''
        zf.writestr('README.md', readme)
        for d in ['app', 'assets', 'config', 'docs', 'source', 'lib']:
            zf.writestr(f'{d}/.gitkeep', '')
    zip_buffer.seek(0)
    return zip_buffer.getvalue()