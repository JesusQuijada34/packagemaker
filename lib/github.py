# -*- coding: utf-8 -*-
import requests

def get_latest_release(token, repo):
    """Get latest release - works with or without token for public repos"""
    try:
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if token:
            headers['Authorization'] = f'token {token}'
        r = requests.get(f'https://api.github.com/repos/{repo}/releases/latest', headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        # If 404 without token, try without auth (public repos)
        if r.status_code == 404 and not token:
            r = requests.get(f'https://api.github.com/repos/{repo}/releases/latest', timeout=10)
            return r.json() if r.status_code == 200 else None
        return None
    except Exception as e:
        print(f"Error fetching release: {e}")
        return None

def get_release_downloads(release):
    dl = {'windows': None, 'linux': None, 'fluthin': 'flarmstore://JesusQuijada34.packagemaker/'}
    for a in release.get('assets', []):
        n = a['name'].lower()
        if 'windows' in n or 'knosthalij' in n: dl['windows'] = a['browser_download_url']
        elif 'linux' in n or 'danenone' in n: dl['linux'] = a['browser_download_url']
    return dl