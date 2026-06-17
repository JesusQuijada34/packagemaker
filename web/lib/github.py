# -*- coding: utf-8 -*-
"""
GitHub integration module for releases
"""

import requests
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_details_xml(xml_path):
    """Parse details.xml to extract version and metadata"""
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
            'year': root.findtext('year') or '2025'
        }
    except:
        return None


def get_latest_release(token, repo):
    """Get latest release info from GitHub"""
    if not token:
        return None
    
    try:
        response = requests.get(
            f'https://api.github.com/repos/{repo}/releases/latest',
            headers={'Authorization': f'token {token}'}
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def get_release_downloads(release_data):
    """Extract download URLs from release assets based on platform"""
    downloads = {
        'windows': None,  # Knosthalij
        'linux': None,    # Danenone
        'fluthin': 'flarmstore://JesusQuijada34.packagemaker/'
    }
    
    assets = release_data.get('assets', [])
    
    for asset in assets:
        name = asset['name'].lower()
        url = asset['browser_download_url']
        
        if 'windows' in name or 'knosthalij' in name:
            downloads['windows'] = url
        elif 'linux' in name or 'danenone' in name:
            downloads['linux'] = url
    
    return downloads


def upload_release_asset(token, repo, release_id, file_path, filename):
    """Upload an asset to a GitHub release"""
    if not token:
        return None
    
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                f'https://uploads.github.com/repos/{repo}/releases/{release_id}/assets',
                headers={
                    'Authorization': f'token {token}',
                    'Content-Type': 'application/octet-stream'
                },
                data=f,
                params={'name': filename}
            )
        
        if response.status_code in [200, 201]:
            return response.json().get('browser_download_url')
        return None
    except:
        return None


def create_release(token, repo, tag_name, name, body, draft=False, prerelease=False):
    """Create a new GitHub release"""
    if not token:
        return None
    
    try:
        # Check if release exists
        response = requests.get(
            f'https://api.github.com/repos/{repo}/releases/tags/{tag_name}',
            headers={'Authorization': f'token {token}'}
        )
        
        if response.status_code == 200:
            return response.json()['id']
        
        # Create new release
        response = requests.post(
            f'https://api.github.com/repos/{repo}/releases',
            headers={'Authorization': f'token {token}'},
            json={
                'tag_name': tag_name,
                'name': name,
                'body': body,
                'draft': draft,
                'prerelease': prerelease
            }
        )
        
        if response.status_code == 201:
            return response.json()['id']
        return None
    except:
        return None


def get_release_notes_content(repo_path):
    """Get content of RELEASE_NOTES.md if exists"""
    release_notes_path = Path(repo_path) / 'RELEASE_NOTES.md'
    if release_notes_path.exists():
        try:
            return release_notes_path.read_text(encoding='utf-8')
        except:
            pass
    return ''