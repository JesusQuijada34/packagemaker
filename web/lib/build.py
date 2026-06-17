# -*- coding: utf-8 -*-
"""
Build module - Integrates FlangCompiler for web-based builds
"""

import os
import sys
import zipfile
import shutil
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent directory to path for FlangCompiler import
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


def extract_project_from_zip(zip_path, extract_to):
    """Extract uploaded project zip"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    # Find the project root (contains details.xml)
    for item in os.listdir(extract_to):
        item_path = os.path.join(extract_to, item)
        if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'details.xml')):
            return item_path
        if os.path.isfile(item_path) and item == 'details.xml':
            return extract_to
    
    return extract_to


def build_project(project_path, target_platform='Linux', log_callback=None):
    """Build project using FlangCompiler (headless mode)"""
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(f"[BUILD] {msg}")
    
    try:
        from lib.BuildThread import FlangCompiler
        
        output_path = Path(_parent_dir) / 'releases'
        output_path.mkdir(parents=True, exist_ok=True)
        
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


def create_project_structure(base_path, project_data):
    """Create project directory structure"""
    project_name = project_data['name']
    project_path = os.path.join(base_path, project_name)
    
    # Create directories
    dirs = ['app', 'assets', 'config', 'docs', 'source', 'lib']
    for d in dirs:
        os.makedirs(os.path.join(project_path, d), exist_ok=True)
    
    # Create main script
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
    
    with open(os.path.join(project_path, f"{project_data['app']}.py"), 'w') as f:
        f.write(main_script)
    
    # Create details.xml
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
    
    with open(os.path.join(project_path, 'details.xml'), 'w') as f:
        f.write(details_xml)
    
    # Create README.md
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
    
    with open(os.path.join(project_path, 'README.md'), 'w') as f:
        f.write(readme)
    
    return project_path


def package_to_zip(project_path, output_path=None):
    """Package a project folder to zip"""
    if output_path is None:
        output_path = str(Path(project_path).parent / f"{Path(project_path).name}.zip")
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_path)
                zipf.write(file_path, arcname)
    
    return output_path