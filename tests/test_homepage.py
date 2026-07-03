import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app


def test_homepage_uses_local_screenshots_and_orange_accent():
    client = app.test_client()
    response = client.get('/')

    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert 'assets/screenshots/gui-1.png' in html
    assert 'assets/screenshots/gui-2.png' in html
    assert '--accent: #ff7a1a;' in html


def test_homepage_detects_browser_language_and_shows_footer_selector():
    client = app.test_client()
    response = client.get('/', headers={'Accept-Language': 'en-US,en;q=0.9'})

    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert 'lang="en"' in html
    assert 'id="language-selector"' in html


def test_download_page_supports_extra_languages():
    client = app.test_client()
    response = client.get('/download', headers={'Accept-Language': 'fr-FR,fr;q=0.9'})

    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert 'value="fr"' in html
    assert 'value="de"' in html
    assert 'Téléchargement' in html or 'Télécharger' in html
