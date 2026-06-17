# -*- coding: utf-8 -*-
"""
Build module - Uses FlangCompiler from lib/BuildThread.py
"""

import os
import sys
import io
import zipfile
import hashlib
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add repo root to path for FlangCompiler import
_parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_repo_root = os.path.dirname(_parent_dir)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)


def parse_details_xml(xml_path):
    """Parse details.xml file and return metadata"""
    try:
        import xml.etree.ElementTree as ET
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
    except Exception as e:
        return {
            'publisher': 'Unknown',
            'app': 'Unknown',
            'name': 'Unknown',
            'version': 'v1.0',
            'platform': 'AlphaCube',
            'author': 'Unknown',
            'description': '',
            'rate': 'All ages',
            'year': datetime.now().year
        }


def build_project(project_path, target_platform='Linux', log_callback=None):
    """Build project using FlangCompiler (headless mode)"""
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(f"[BUILD] {msg}")
    
    try:
        from lib.BuildThread import FlangCompiler
        
        # Use temp directory for output
        output_path = Path(tempfile.mkdtemp(prefix='pm_build_'))
        
        compiler = FlangCompiler(
            repo_path=Path(project_path),
            output_path=output_path,
            log_callback=log
        )
        
        result = compiler.run(build_mode="portable")
        return str(result) if result else None
    except ImportError as e:
        log(f"[ERROR] Could not import FlangCompiler: {e}")
        return None
    except Exception as e:
        log(f"[ERROR] Build failed: {e}")
        return None


def create_project_zip(project_data):
    """Create project structure in memory and return as zip bytes"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Main script
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
        
        # details.xml
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
        
        # README.md
        readme = f'''# {project_data['title']}

{project_data.get('description', 'A Fluthin application')}

## Information
- **Publisher:** {project_data['publisher']}
- **Author:** {project_data['author']}
- **Version:** {project_data['version']}
- **Platform:** {project_data['platform']}

## Installation
Download the `.iflapp` file and install using Package Maker or Fluthin Store.
'''
        zf.writestr('README.md', readme)
        
        # Create directory structure
        dirs = ['app', 'assets', 'config', 'docs', 'source', 'lib']
        for d in dirs:
            zf.writestr(f'{d}/.gitkeep', '')
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def extract_project_from_zip(zip_bytes, project_name):
    """Extract project from zip bytes to temp directory"""
    temp_dir = Path(tempfile.mkdtemp(prefix=f'pm_{project_name}_'))
    zip_buffer = io.BytesIO(zip_bytes)
    
    with zipfile.ZipFile(zip_buffer, 'r') as zf:
        zf.extractall(temp_dir)
    
    # Find project root
    for item in temp_dir.iterdir():
        if item.is_dir() and (item / 'details.xml').exists():
            return str(item)
        if item.name == 'details.xml':
            return str(temp_dir)
    
    return str(temp_dir)


def list_project_files(project_path):
    """List all files in a project"""
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
    return files


def save_file(project_path, file_path, content):
    """Save a file in the project"""
    full_path = os.path.join(project_path, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)


def project_to_zip(project_path):
    """Convert project directory to zip bytes"""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_path)
                zf.write(file_path, arcname)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()