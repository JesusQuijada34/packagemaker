import os
import requests
import xml.etree.ElementTree as ET
from flask import Flask, render_template, jsonify, request, Response, session, send_from_directory, g
import markdown
import sqlite3
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.secret_key = 'pm-pwa-secret-2026'

SUPPORTED_LANGUAGES = {
    'es': {'name': 'Español', 'native': 'Español'},
    'en': {'name': 'English', 'native': 'English'},
    'pt': {'name': 'Português', 'native': 'Português'},
    'fr': {'name': 'Français', 'native': 'Français'},
    'de': {'name': 'Deutsch', 'native': 'Deutsch'},
    'it': {'name': 'Italiano', 'native': 'Italiano'},
    'ja': {'name': '日本語', 'native': '日本語'},
    'zh': {'name': '中文', 'native': '中文'},
}

TRANSLATIONS = {
    'es': {
        'nav_home': 'Inicio',
        'nav_download': 'Descargas',
        'nav_release_notes': 'Notas',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. Creado por JesusQuijada34.',
        'footer_language': 'Idioma',
        'back_home': 'Volver al inicio',
        'hero_badge': '✨ Nueva Versión v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'Tu IDE Profesional para Python ha evolucionado. Crea, empaqueta y distribuye aplicaciones Python con una experiencia moderna y eficiente inspirada en Windows 11.',
        'hero_download': 'Descargar Ahora',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': 'Interfaz intuitiva y potente',
        'section_interface_subtitle': 'Barra de título personalizada Leviathan-UI con efectos visuales acrílico y mica.',
        'download_title': 'Obtén la Suite',
        'download_intro': 'Descarga directa para tu plataforma o alternativas si no hay versión específica.',
        'download_direct_title': 'Descarga Directa',
        'download_android_title': 'Optimizado para Termux',
        'download_android_desc': 'Instalación directa y automatizada para dispositivos móviles Android.',
        'download_android_hint': 'Copia y pega este comando en tu terminal Termux.',
        'download_no_direct_title': 'No hay versión directa',
        'download_no_direct_desc': 'No existe un archivo .iflapp para tu plataforma, pero puedes:',
        'download_source_code': 'Código Fuente',
        'download_versions': 'Ver Versiones',
        'download_available_versions': 'Versiones Disponibles',
        'download_requirements': 'Requisitos',
        'download_specs': 'Especificaciones',
        'download_copy_command': 'Copiar comando',
        'error_404_title': 'Página No Encontrada',
        'error_404_desc': 'La página que buscas se ha perdido en el espacio digital.',
        'error_500_title': 'Error Interno del Servidor',
        'error_500_desc': 'Algo salió mal en nuestro servidor. Estamos trabajando para resolverlo.',
        'error_403_title': 'Acceso Prohibido',
        'error_back_home': 'Volver al Inicio',
        'error_downloads': 'Descargas',
        'pwa_status': 'Estado del Sistema',
        'pwa_install': 'INSTALAR APP IDE',
        'pwa_home': 'Inicio',
        'pwa_downloads': 'Descargas',
        'pwa_notes': 'Notas',
        'pwa_issues': 'Issues',
        'pwa_faq': 'FAQ',
    },
    'en': {
        'nav_home': 'Home',
        'nav_download': 'Downloads',
        'nav_release_notes': 'Notes',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. Crafted by JesusQuijada34.',
        'footer_language': 'Language',
        'back_home': 'Back to home',
        'hero_badge': '✨ New Version v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'Your professional Python IDE has evolved. Create, package and distribute Python apps with a modern, efficient experience inspired by Windows 11.',
        'hero_download': 'Download Now',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': 'Intuitive and powerful interface',
        'section_interface_subtitle': 'Custom Leviathan-UI title bar with acrylic and mica visual effects.',
        'download_title': 'Get the Suite',
        'download_intro': 'Direct download for your platform or alternatives if a specific version is unavailable.',
        'download_direct_title': 'Direct Download',
        'download_android_title': 'Optimized for Termux',
        'download_android_desc': 'Direct and automated installation for Android mobile devices.',
        'download_android_hint': 'Copy and paste this command into your Termux terminal.',
        'download_no_direct_title': 'No direct version available',
        'download_no_direct_desc': 'There is no .iflapp file for your platform, but you can:',
        'download_source_code': 'Source Code',
        'download_versions': 'View Versions',
        'download_available_versions': 'Available versions',
        'download_requirements': 'Requirements',
        'download_specs': 'Specifications',
        'download_copy_command': 'Copy command',
        'error_404_title': 'Page Not Found',
        'error_404_desc': 'The page you are looking for has drifted into the digital void.',
        'error_500_title': 'Internal Server Error',
        'error_500_desc': 'Something went wrong on our server. We are working on it.',
        'error_403_title': 'Access Forbidden',
        'error_back_home': 'Back to Home',
        'error_downloads': 'Downloads',
        'pwa_status': 'System Status',
        'pwa_install': 'INSTALL IDE APP',
        'pwa_home': 'Home',
        'pwa_downloads': 'Downloads',
        'pwa_notes': 'Notes',
        'pwa_issues': 'Issues',
        'pwa_faq': 'FAQ',
    },
    'pt': {
        'nav_home': 'Início',
        'nav_download': 'Downloads',
        'nav_release_notes': 'Notas',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. Criado por JesusQuijada34.',
        'footer_language': 'Idioma',
        'back_home': 'Voltar ao início',
        'hero_badge': '✨ Nova Versão v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'Seu IDE profissional para Python evoluiu. Crie, empacote e distribua aplicativos Python com uma experiência moderna e eficiente inspirada no Windows 11.',
        'hero_download': 'Baixar agora',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': 'Interface intuitiva e poderosa',
        'section_interface_subtitle': 'Barra de título personalizada do Leviathan-UI com efeitos visuais de acrílico e mica.',
        'download_title': 'Obtenha a suíte',
        'download_intro': 'Download direto para sua plataforma ou alternativas se nenhuma versão específica estiver disponível.',
        'download_direct_title': 'Download direto',
        'download_android_title': 'Otimizando para Termux',
        'download_android_desc': 'Instalação direta e automatizada para dispositivos móveis Android.',
        'download_android_hint': 'Copie e cole este comando no seu terminal Termux.',
        'download_no_direct_title': 'Nenhuma versão direta disponível',
        'download_no_direct_desc': 'Não existe um arquivo .iflapp para a sua plataforma, mas você pode:',
        'download_source_code': 'Código Fonte',
        'download_versions': 'Ver versões',
        'download_available_versions': 'Versões disponíveis',
        'download_requirements': 'Requisitos',
        'download_specs': 'Especificações',
        'download_copy_command': 'Copiar comando',
        'error_404_title': 'Página não encontrada',
        'error_404_desc': 'A página que você procura se perdeu no espaço digital.',
        'error_500_title': 'Erro interno do servidor',
        'error_500_desc': 'Algo deu errado em nosso servidor. Estamos trabalhando para resolver isso.',
        'error_403_title': 'Acesso proibido',
        'error_back_home': 'Voltar ao início',
        'error_downloads': 'Downloads',
        'pwa_status': 'Estado do sistema',
        'pwa_install': 'INSTALAR APP IDE',
        'pwa_home': 'Início',
        'pwa_downloads': 'Downloads',
        'pwa_notes': 'Notas',
        'pwa_issues': 'Issues',
        'pwa_faq': 'FAQ',
    },
    'fr': {
        'nav_home': 'Accueil',
        'nav_download': 'Téléchargements',
        'nav_release_notes': 'Notes',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. Créé par JesusQuijada34.',
        'footer_language': 'Langue',
        'back_home': 'Retour à l’accueil',
        'hero_badge': '✨ Nouvelle version v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'Votre IDE Python professionnel a évolué. Créez, empaquetez et distribuez des applications Python avec une expérience moderne et efficace inspirée de Windows 11.',
        'hero_download': 'Télécharger',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': 'Interface intuitive et puissante',
        'section_interface_subtitle': 'Barre de titre Leviathan-UI personnalisée avec des effets visuels en acrylique et mica.',
        'download_title': 'Obtenez la suite',
        'download_intro': 'Téléchargement direct pour votre plateforme ou alternatives si aucune version spécifique n’est disponible.',
        'download_direct_title': 'Téléchargement direct',
        'download_android_title': 'Optimisé pour Termux',
        'download_android_desc': 'Installation directe et automatisée pour les appareils Android.',
        'download_android_hint': 'Copiez et collez cette commande dans votre terminal Termux.',
        'download_no_direct_title': 'Aucune version directe disponible',
        'download_no_direct_desc': 'Aucun fichier .iflapp n’existe pour votre plateforme, mais vous pouvez :',
        'download_source_code': 'Code source',
        'download_versions': 'Voir les versions',
        'download_available_versions': 'Versions disponibles',
        'download_requirements': 'Prérequis',
        'download_specs': 'Spécifications',
        'download_copy_command': 'Copier la commande',
        'error_404_title': 'Page introuvable',
        'error_404_desc': 'La page que vous recherchez s’est perdue dans le vide numérique.',
        'error_500_title': 'Erreur interne du serveur',
        'error_500_desc': 'Quelque chose s’est mal passé sur notre serveur. Nous travaillons à résoudre ce problème.',
        'error_403_title': 'Accès refusé',
        'error_back_home': 'Retour à l’accueil',
        'error_downloads': 'Téléchargements',
        'pwa_status': 'État du système',
        'pwa_install': 'INSTALLER L’APP IDE',
        'pwa_home': 'Accueil',
        'pwa_downloads': 'Téléchargements',
        'pwa_notes': 'Notes',
        'pwa_issues': 'Issues',
        'pwa_faq': 'FAQ',
    },
    'de': {
        'nav_home': 'Startseite',
        'nav_download': 'Downloads',
        'nav_release_notes': 'Hinweise',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. Erstellt von JesusQuijada34.',
        'footer_language': 'Sprache',
        'back_home': 'Zurück zur Startseite',
        'hero_badge': '✨ Neue Version v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'Ihre professionelle Python-IDE hat sich weiterentwickelt. Erstellen, verpacken und verteilen Sie Python-Apps mit einer modernen und effizienten Erfahrung, inspiriert von Windows 11.',
        'hero_download': 'Jetzt herunterladen',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': 'Intuitive und leistungsstarke Oberfläche',
        'section_interface_subtitle': 'Benutzerdefinierte Leviathan-UI-Titelleiste mit Acryl- und Mica-Effekten.',
        'download_title': 'Erhalten Sie die Suite',
        'download_intro': 'Direkter Download für Ihre Plattform oder Alternativen, falls keine spezifische Version verfügbar ist.',
        'download_direct_title': 'Direkter Download',
        'download_android_title': 'Optimiert für Termux',
        'download_android_desc': 'Direkte und automatisierte Installation für Android-Geräte.',
        'download_android_hint': 'Kopieren Sie diesen Befehl und fügen Sie ihn in Ihr Termux-Terminal ein.',
        'download_no_direct_title': 'Keine direkte Version verfügbar',
        'download_no_direct_desc': 'Es gibt keine .iflapp-Datei für Ihre Plattform, aber Sie können:',
        'download_source_code': 'Quellcode',
        'download_versions': 'Versionen ansehen',
        'download_available_versions': 'Verfügbare Versionen',
        'download_requirements': 'Anforderungen',
        'download_specs': 'Spezifikationen',
        'download_copy_command': 'Befehl kopieren',
        'error_404_title': 'Seite nicht gefunden',
        'error_404_desc': 'Die gesuchte Seite ist im digitalen Nichts verschwunden.',
        'error_500_title': 'Interner Serverfehler',
        'error_500_desc': 'Etwas ist auf unserem Server schiefgelaufen. Wir arbeiten daran.',
        'error_403_title': 'Zugriff verboten',
        'error_back_home': 'Zurück zur Startseite',
        'error_downloads': 'Downloads',
        'pwa_status': 'Systemstatus',
        'pwa_install': 'IDE-APP INSTALLIEREN',
        'pwa_home': 'Startseite',
        'pwa_downloads': 'Downloads',
        'pwa_notes': 'Hinweise',
        'pwa_issues': 'Issues',
        'pwa_faq': 'FAQ',
    },
    'it': {
        'nav_home': 'Home',
        'nav_download': 'Download',
        'nav_release_notes': 'Note',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. Creato da JesusQuijada34.',
        'footer_language': 'Lingua',
        'back_home': 'Torna alla home',
        'hero_badge': '✨ Nuova versione v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'Il tuo IDE Python professionale si è evoluto. Crea, impacchetta e distribuisci app Python con un’esperienza moderna ed efficiente ispirata a Windows 11.',
        'hero_download': 'Scarica ora',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': 'Interfaccia intuitiva e potente',
        'section_interface_subtitle': 'Barra del titolo Leviathan-UI personalizzata con effetti visivi in acrilico e mica.',
        'download_title': 'Ottieni la suite',
        'download_intro': 'Download diretto per la tua piattaforma o alternative se non è disponibile una versione specifica.',
        'download_direct_title': 'Download diretto',
        'download_android_title': 'Ottimizzato per Termux',
        'download_android_desc': 'Installazione diretta e automatizzata per dispositivi mobili Android.',
        'download_android_hint': 'Copia e incolla questo comando nel terminale Termux.',
        'download_no_direct_title': 'Nessuna versione diretta disponibile',
        'download_no_direct_desc': 'Non esiste un file .iflapp per la tua piattaforma, ma puoi:',
        'download_source_code': 'Codice sorgente',
        'download_versions': 'Vedi versioni',
        'download_available_versions': 'Versioni disponibili',
        'download_requirements': 'Requisiti',
        'download_specs': 'Specifiche',
        'download_copy_command': 'Copia comando',
        'error_404_title': 'Pagina non trovata',
        'error_404_desc': 'La pagina che stai cercando si è persa nel vuoto digitale.',
        'error_500_title': 'Errore interno del server',
        'error_500_desc': 'Qualcosa è andato storto sul nostro server. Stiamo lavorando per risolverlo.',
        'error_403_title': 'Accesso vietato',
        'error_back_home': 'Torna alla home',
        'error_downloads': 'Download',
        'pwa_status': 'Stato del sistema',
        'pwa_install': 'INSTALLA L’APP IDE',
        'pwa_home': 'Home',
        'pwa_downloads': 'Download',
        'pwa_notes': 'Note',
        'pwa_issues': 'Issues',
        'pwa_faq': 'FAQ',
    },
    'ja': {
        'nav_home': 'ホーム',
        'nav_download': 'ダウンロード',
        'nav_release_notes': 'ノート',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering. JesusQuijada34 によって作成されました。',
        'footer_language': '言語',
        'back_home': 'ホームに戻る',
        'hero_badge': '✨ 新バージョン v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': 'プロフェッショナルな Python IDE が進化しました。Windows 11 に着想を得た現代的で効率的な体験で Python アプリを作成、パッケージ化、配布します。',
        'hero_download': '今すぐダウンロード',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': '直感的で強力なインターフェース',
        'section_interface_subtitle': 'アクリルとミカの視覚効果を備えたカスタム Leviathan-UI タイトルバー。',
        'download_title': 'スイートを入手',
        'download_intro': 'お使いのプラットフォーム向けの直接ダウンロード、または特定バージョンがない場合の代替手段。',
        'download_direct_title': '直接ダウンロード',
        'download_android_title': 'Termux 向け最適化',
        'download_android_desc': 'Android モバイル端末向けの直接自動インストール。',
        'download_android_hint': 'このコマンドを Termux ターミナルにコピーして貼り付けてください。',
        'download_no_direct_title': '直接ダウンロード版はありません',
        'download_no_direct_desc': 'お使いのプラットフォーム用の .iflapp ファイルはありませんが、次の方法があります:',
        'download_source_code': 'ソースコード',
        'download_versions': 'バージョンを見る',
        'download_available_versions': '利用可能なバージョン',
        'download_requirements': '要件',
        'download_specs': '仕様',
        'download_copy_command': 'コマンドをコピー',
        'error_404_title': 'ページが見つかりません',
        'error_404_desc': 'お探しのページはデジタルの空の彼方に消えました。',
        'error_500_title': 'サーバー内部エラー',
        'error_500_desc': 'サーバーで問題が発生しました。対応中です。',
        'error_403_title': 'アクセスが拒否されました',
        'error_back_home': 'ホームに戻る',
        'error_downloads': 'ダウンロード',
        'pwa_status': 'システム状態',
        'pwa_install': 'IDE アプリをインストール',
        'pwa_home': 'ホーム',
        'pwa_downloads': 'ダウンロード',
        'pwa_notes': 'ノート',
        'pwa_issues': 'Issues',
        'pwa_faq': 'FAQ',
    },
    'zh': {
        'nav_home': '首页',
        'nav_download': '下载',
        'nav_release_notes': '说明',
        'nav_issues': 'Issues',
        'nav_faq': 'FAQ',
        'footer_text': '© 2026 Influent OS Engineering。由 JesusQuijada34 创建。',
        'footer_language': '语言',
        'back_home': '返回首页',
        'hero_badge': '✨ 新版本 v3.2.7-26.05-20.13',
        'hero_title': 'Influent Package Maker',
        'hero_subtitle': '专业的 Python IDE 已经升级。借鉴 Windows 11 的现代高效体验，创建、打包和分发 Python 应用。',
        'hero_download': '立即下载',
        'hero_github': 'GitHub',
        'hero_platform_windows': 'Windows',
        'hero_platform_android': 'Android',
        'hero_platform_linux': 'Linux',
        'section_interface_title': '直观且强大的界面',
        'section_interface_subtitle': '具有亚克力和云母视觉效果的定制 Leviathan-UI 标题栏。',
        'download_title': '获取套件',
        'download_intro': '为您的平台提供直接下载，或在没有特定版本时提供替代方案。',
        'download_direct_title': '直接下载',
        'download_android_title': '针对 Termux 优化',
        'download_android_desc': '适用于 Android 移动设备的直接自动安装。',
        'download_android_hint': '将此命令复制并粘贴到您的 Termux 终端中。',
        'download_no_direct_title': '没有可用的直接版本',
        'download_no_direct_desc': '您的平台没有 .iflapp 文件，但您可以：',
        'download_source_code': '源代码',
        'download_versions': '查看版本',
        'download_available_versions': '可用版本',
        'download_requirements': '系统要求',
        'download_specs': '规格',
        'download_copy_command': '复制命令',
        'error_404_title': '页面未找到',
        'error_404_desc': '您寻找的页面已经消失在数字空间中。',
        'error_500_title': '服务器内部错误',
        'error_500_desc': '我们的服务器出现了问题。我们正在处理。',
        'error_403_title': '访问被拒绝',
        'error_back_home': '返回首页',
        'error_downloads': '下载',
        'pwa_status': '系统状态',
        'pwa_install': '安装 IDE 应用',
        'pwa_home': '首页',
        'pwa_downloads': '下载',
        'pwa_notes': '说明',
        'pwa_issues': 'Issues',
        'pwa_faq': 'FAQ',
    },
}


def normalize_language(lang_code: str | None) -> str:
    if not lang_code:
        return 'es'
    code = str(lang_code).strip().lower().replace('_', '-')
    if code.startswith(('en', 'en-us', 'en-gb')):
        return 'en'
    if code.startswith(('pt', 'pt-br', 'pt-pt')):
        return 'pt'
    if code.startswith(('fr', 'fr-fr', 'fr-ca')):
        return 'fr'
    if code.startswith(('de', 'de-de')):
        return 'de'
    if code.startswith(('it', 'it-it')):
        return 'it'
    if code.startswith(('ja', 'ja-jp')):
        return 'ja'
    if code.startswith(('zh', 'zh-cn', 'zh-hk', 'zh-tw')):
        return 'zh'
    if code.startswith(('es', 'es-es', 'es-mx')):
        return 'es'
    return 'es'


def resolve_language(request_obj) -> str:
    requested = (
        request_obj.args.get('lang')
        or session.get('lang')
        or request_obj.cookies.get('lang')
        or request_obj.headers.get('X-Language')
        or request_obj.accept_languages.best_match(list(SUPPORTED_LANGUAGES.keys()))
        or 'es'
    )
    return normalize_language(requested)


@app.before_request
def apply_language():
    lang_code = resolve_language(request)
    session['lang'] = lang_code
    g.lang_code = lang_code
    g.lang_name = SUPPORTED_LANGUAGES[lang_code]['name']
    g.translations = TRANSLATIONS[lang_code]
    g.available_languages = SUPPORTED_LANGUAGES


@app.after_request
def persist_language(response):
    if hasattr(g, 'lang_code'):
        response.set_cookie('lang', g.lang_code, max_age=60 * 60 * 24 * 365, path='/', samesite='Lax')
    return response


@app.context_processor
def inject_language_context():
    return {
        'lang_code': getattr(g, 'lang_code', 'es'),
        'lang_name': getattr(g, 'lang_name', 'Español'),
        'translations': getattr(g, 'translations', TRANSLATIONS['es']),
        'available_languages': getattr(g, 'available_languages', SUPPORTED_LANGUAGES),
    }

# Configuración
GITHUB_REPO = "JesusQuijada34/packagemaker"
XML_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/details.xml"
RELEASE_NOTES_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/RELEASE_NOTES.md"
FAQ_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/FAQ.md"
DB_PATH = 'analytics.db'

# Inicializar Base de Datos
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS visits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  session_id TEXT,
                  timestamp DATETIME,
                  path TEXT,
                  platform TEXT,
                  ip TEXT,
                  duration INTEGER DEFAULT 0,
                  bounced BOOLEAN DEFAULT 1)''')
    conn.commit()
    conn.close()

init_db()

@app.before_request
def track_visit():
    if not request.path.startswith('/static') and not request.path.startswith('/admin') and not request.path.startswith('/api/track'):
        if 'session_id' not in session: session['session_id'] = str(uuid.uuid4())
        try:
            ua = request.headers.get('User-Agent', '').lower()
            platform = 'Desktop'
            if 'android' in ua: platform = 'Android'
            elif 'windows' in ua: platform = 'Windows'
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO visits (session_id, timestamp, path, platform, ip) VALUES (?, ?, ?, ?, ?)",
                      (session['session_id'], datetime.now(), request.path, platform, request.remote_addr))
            conn.commit()
            conn.close()
        except Exception as e: print(f"Error tracking: {e}")

@app.route('/api/track/update', methods=['POST'])
def update_track():
    data = request.json
    session_id = session.get('session_id')
    if session_id and data:
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("UPDATE visits SET duration = ?, bounced = ? WHERE session_id = ? ORDER BY id DESC LIMIT 1",
                      (data.get('duration', 0), 0 if data.get('duration', 0) > 5 else 1, session_id))
            conn.commit()
            conn.close()
        except: pass
    return jsonify({"status": "ok"})

# PWA Assets
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def sw():
    return send_from_directory('static', 'sw.js')

@app.route('/app/<path:filename>')
def app_assets(filename):
    return send_from_directory('app', filename)

@app.route('/assets/<path:filename>')
def site_assets(filename):
    return send_from_directory('assets', filename)

def get_xml_metadata():
    try:
        response = requests.get(XML_URL, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            return {child.tag: child.text for child in root}
    except Exception as e:
        print(f"Error fetching XML: {e}")
    return {"version": "v3.2.7", "name": "Package Maker"}


def get_latest_release_version():
    try:
        response = requests.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", timeout=8)
        if response.status_code == 200:
            return response.json().get("tag_name") or get_xml_metadata().get("version", "v3.2.7")
    except Exception as e:
        print(f"Error fetching latest release version: {e}")
    return get_xml_metadata().get("version", "v3.2.7")


def classify_download_asset(name: str):
    lowered = (name or "").lower()
    if any(token in lowered for token in ["danenone", "linux", "appimage"]):
        return "linux", "linux"
    if any(token in lowered for token in ["knosthalij", "windows", "exe"]):
        return "windows", "windows"
    if "android" in lowered:
        return "android", "android"
    return "other", "other"


def get_release_info():
    """Get all releases with their assets for download verification"""
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            releases = response.json()
            all_downloads = []
            for release in releases[:5]:  # Latest 5 releases
                version = release.get("tag_name", "")
                assets = release.get("assets", [])
                for asset in assets:
                    name = asset.get("name", "") or ""
                    platform_key = classify_download_asset(name)[1]
                    platform = {
                        "linux": "Linux",
                        "windows": "Windows",
                        "android": "Android",
                    }.get(platform_key, "Other")
                    url = asset.get("browser_download_url", "")
                    all_downloads.append({
                        "name": asset.get("name"),
                        "url": url,
                        "platform": platform,
                        "platform_key": platform_key,
                        "version": version,
                        "size": f"{asset.get('size', 0) / (1024*1024):.2f} MB"
                    })
            return all_downloads
    except Exception as e:
        print(f"Error fetching releases: {e}")
    return []

def check_iflapp_exists(url):
    """Check if an iflapp file exists at the given URL."""
    try:
        response = requests.get(url, timeout=15, allow_redirects=True, stream=True, headers={"User-Agent": "Mozilla/5.0"})
        return response.status_code < 400
    except Exception:
        return False

def get_github_releases():
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            version = data.get("tag_name", "")
            assets = data.get("assets", [])
            downloads = []
            for asset in assets:
                name = asset.get("name", "") or ""
                platform_key = classify_download_asset(name)[1]
                platform = {
                    "linux": "Linux",
                    "windows": "Windows",
                    "android": "Android",
                }.get(platform_key, "Other")
                downloads.append({"name": asset.get("name"), "url": asset.get("browser_download_url"), "platform": platform, "size": f"{asset.get('size', 0) / (1024*1024):.2f} MB"})
            return version, downloads
    except Exception as e:
        print(f"Error fetching releases: {e}")
    return "v3.2.7", []

def get_download_for_platform(user_agent):
    """Get download info based on platform detection, checking the latest release assets."""
    ua = user_agent.lower()
    all_downloads = get_release_info()

    if "android" in ua or "mobile" in ua:
        detected_platform = "android"
        preferred_keys = []
    elif "win" in ua or "windows" in ua:
        detected_platform = "windows"
        preferred_keys = ["windows"]
    elif "linux" in ua or "ubuntu" in ua or "debian" in ua:
        detected_platform = "linux"
        preferred_keys = ["linux"]
    else:
        detected_platform = "desktop"
        preferred_keys = ["windows", "linux"]

    direct_download = None
    for preferred_key in preferred_keys:
        for dl in all_downloads:
            if dl["platform_key"] == preferred_key:
                if check_iflapp_exists(dl["url"]):
                    direct_download = dl
                    break
        if direct_download:
            break

    download_status = "available"
    if direct_download is None and all_downloads:
        fallback_download = next((dl for dl in all_downloads if check_iflapp_exists(dl["url"])), None)
        if fallback_download:
            direct_download = fallback_download
        else:
            download_status = "unavailable"

    alternatives = []
    for dl in all_downloads[:6]:
        if dl != direct_download:
            alternatives.append(dl)

    return {
        "detected_platform": detected_platform,
        "direct_download": direct_download,
        "download_status": download_status,
        "alternatives": alternatives,
        "all_downloads": all_downloads
    }

@app.route('/')
def index():
    print(f"DEBUG: Accessing index from {request.remote_addr}")
    metadata = get_xml_metadata()
    version = get_latest_release_version()
    ua = request.headers.get('User-Agent', '').lower()
    return render_template('index.html', metadata=metadata, version=version, is_android='android' in ua)

@app.route('/download')
def download():
    print(f"DEBUG: Accessing download from {request.remote_addr}")
    metadata = get_xml_metadata()
    version = get_latest_release_version() or metadata.get("version", "v3.2.7")
    ua = request.headers.get('User-Agent', '')
    
    # Get download info with platform detection and existence check
    download_info = get_download_for_platform(ua)
    
    return render_template(
        'download.html', 
        metadata=metadata, 
        version=version, 
        is_android=download_info["detected_platform"] == "android",
        download_info=download_info
    )

@app.route('/faq')
def faq_page():
    try:
        response = requests.get(FAQ_URL, timeout=5)
        content = response.text if response.status_code == 200 else "# FAQ\nNo se pudo cargar el contenido."
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Preguntas Frecuentes", content=html_content)
    except Exception as e:
        print(f"Error loading FAQ: {e}")
        return render_template('error.html', code=500, message="Error al cargar FAQ"), 500

@app.route('/release-notes')
def notes():
    try:
        response = requests.get(RELEASE_NOTES_URL, timeout=5)
        content = response.text if response.status_code == 200 else "# Release Notes"
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Notas de Versión", content=html_content)
    except Exception as e:
        print(f"Error loading notes: {e}")
        return render_template('error.html', code=500, message="Error al cargar Notas"), 500

@app.route('/issues')
def issues_page():
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues?state=open"
        response = requests.get(api_url, timeout=5)
        issues = response.json() if response.status_code == 200 else []
        
        content = "# Problemas Conocidos y Reportes\n\n"
        if not issues:
            content += "Actualmente no hay problemas abiertos reportados. Si encuentras un error, por favor [infórmalo en GitHub](https://github.com/JesusQuijada34/packagemaker/issues).\n"
        else:
            for issue in issues:
                if not issue.get('pull_request'):
                    content += f"### ⚠️ {issue.get('title')}\n"
                    content += f"- **Estado**: {issue.get('state')}\n"
                    content += f"- **Reportado por**: {issue.get('user', {}).get('login')}\n"
                    content += f"- [Ver en GitHub]({issue.get('html_url')})\n\n"
        
        html_content = markdown.markdown(content, extensions=['extra', 'codehilite'])
        return render_template('page.html', title="Issues & Soporte", content=html_content)
    except Exception as e:
        print(f"Error loading issues: {e}")
        return render_template('error.html', code=500, message="Error al cargar Issues"), 500

@app.route('/pwaMode')
def pwa_mode():
    mode = request.args.get('id', 'desktop')
    metadata = get_xml_metadata()
    version, downloads = get_github_releases()
    return render_template('pwa.html', mode=mode, metadata=metadata, version=version, downloads=downloads)

@app.route('/api/download.sh')
def download_sh():
    script = """#!/bin/bash
# Package Maker - Auto Installer
RED='\\033[0;31m'
GREEN='\\033[0;32m'
CYAN='\\033[0;36m'
YELLOW='\\033[1;33m'
NC='\\033[0m'
clear
echo -e "${CYAN}====================================================${NC}"
echo -e "${CYAN}       PACKAGE MAKER - INSTALADOR AUTOMÁTICO        ${NC}"
echo -e "${CYAN}====================================================${NC}"
if [ -d "/data/data/com.termux/files/home" ]; then ENV="termux"; else ENV="linux"; fi
if [ "$ENV" == "termux" ]; then pkg update -y && pkg upgrade -y && pkg install -y git python python-pip libexpat openssl
else sudo apt update -y && sudo apt install -y git python3 python3-pip libexpat1; fi
git clone -b main https://github.com/JesusQuijada34/packagemaker.git
cd packagemaker
pip3 install -r lib/requirements.txt
echo -e "${GREEN}INSTALACIÓN COMPLETADA. Inicia con: python3 packagemaker.py${NC}"
"""
    return Response(script, mimetype='text/x-shellscript')

@app.route('/admin/stats')
def admin_stats():
    print(f"DEBUG: Accessing admin_stats from {request.remote_addr}")
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM visits"); total = c.fetchone()[0]
        c.execute("SELECT AVG(duration) FROM visits WHERE duration > 0"); avg_time = c.fetchone()[0] or 0
        c.execute("SELECT platform, COUNT(*) FROM visits GROUP BY platform"); platforms = dict(c.fetchall())
        c.execute("SELECT path, COUNT(*) FROM visits GROUP BY path ORDER BY COUNT(*) DESC LIMIT 5"); paths = c.fetchall()
        c.execute("SELECT (COUNT(CASE WHEN bounced = 1 THEN 1 END) * 100.0 / COUNT(*)) FROM visits"); bounce = c.fetchone()[0] or 0
        c.execute("SELECT timestamp, path, platform, duration, bounced FROM visits ORDER BY id DESC LIMIT 20"); recent = c.fetchall()
        conn.close()
        return render_template('stats.html', total=total, avg_time=round(avg_time, 1), platforms=platforms, paths=paths, bounce=round(bounce, 1), recent=recent)
    except Exception as e:
        print(f"DEBUG ERROR in admin_stats: {e}")
        return render_template('error.html', code=500, message=f"Error en base de datos: {e}"), 500

# Error Handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, path=request.path), 404

@app.errorhandler(500)
def internal_error(e):
    message = getattr(e, 'description', 'Error Interno del Servidor')
    return render_template('error.html', code=500, message=message), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403), 403

@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code=400), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
