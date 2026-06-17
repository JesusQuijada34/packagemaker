# -*- coding: utf-8 -*-
import requests

def get_latest_release(token, repo):
    if not token: return None
    try:
        r = requests.get(f'https://api.github.com/repos/{repo}/releases/latest', headers={'Authorization': f'token {token}'})
        return r.json() if r.status_code == 200 else None
    except: return None

def get_release_downloads(release):
    dl = {'windows': None, 'linux': None, 'fluthin': 'flarmstore://JesusQuijada34.packagemaker/'}
    for a in release.get('assets', []):
        n = a['name'].lower()
        if 'windows' in n or 'knosthalij' in n: dl['windows'] = a['browser_download_url']
        elif 'linux' in n or 'danenone' in n: dl['linux'] = a['browser_download_url']
    return dl