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
        'feature_projects_title': 'Gestión de Proyectos',
        'feature_projects_desc': 'Sistema de compilación avanzada con detección automática de scripts.',
        'feature_projects_item_1': 'Integración con <code>.gitignore</code>',
        'feature_projects_item_2': 'Limpieza automática post-compilación',
        'feature_projects_item_3': 'Gestión de dependencias',
        'feature_security_title': 'Blindado de Código',
        'feature_security_desc': 'Protege tu propiedad intelectual con métodos avanzados.',
        'feature_security_item_1': '<strong>Simple Blind:</strong> Empaqueta en <code>.iflappb</code>',
        'feature_security_item_2': '<strong>Super Blind:</strong> Separación de clases + encriptación',
        'feature_build_title': 'Compilación Avanzada',
        'feature_build_desc': 'Detecta automáticamente scripts candidatos, gestiona dependencias y minifica tu código.',
        'feature_build_item_1': '✓ gitignore integrado',
        'feature_build_item_2': '✓ Limpieza automática',
        'feature_build_item_3': '✓ Paquetes ligeros',
        'feature_multiplatform_title': 'Multi-Plataforma',
        'feature_multiplatform_desc': 'Genera ejecutables para cualquier plataforma desde un solo código.',
        'feature_apps_title': 'Gestor de Apps',
        'feature_apps_desc': 'Administra tus proyectos locales y aplicaciones instaladas.',
        'feature_config_title': 'Configuración',
        'feature_config_desc': 'Control total sobre rutas, idioma y personalización.',
        'feature_moonfix_title': 'Sanación Profunda de Proyectos',
        'feature_moonfix_desc': 'Tu aliada para mantener la salud de tus proyectos. Realiza una sanación profunda, escaneando y reparando inconsistencias.',
        'feature_about_title': 'Acerca de Influent Package Maker',
        'feature_about_framework': 'Framework',
        'feature_about_framework_value': 'Qt 6.11.1',
        'feature_about_ui': 'Sistema de UI',
        'feature_about_ui_value': 'Leviathan',
        'feature_about_license': 'Licencia',
        'feature_about_license_value': 'GNU GPL v3',
        'feature_about_developer': 'Desarrollador',
        'feature_about_developer_value': 'Jesús Quijada',
        'feature_cli_title': 'Terminal (CLI)',
        'feature_cli_desc': 'Potente interfaz de línea de comandos para automatizar tareas e integrar en scripts CI/CD.',
        'feature_news_title': 'Novedades v3.2.7',
        'feature_news_item_1_title': 'Editores Extendidos',
        'feature_news_item_1_desc': 'Zed, Fleet, Emacs, Geany, Kate, Gedit',
        'feature_news_item_2_title': 'Iconos en Linux',
        'feature_news_item_2_desc': 'Renderizado mejorado para Ubuntu',
        'feature_news_item_3_title': 'Correcciones',
        'feature_news_item_3_desc': 'TypeError, fondo blanco, gradientes',
        'cta_title': '¿Listo para el siguiente nivel?',
        'cta_desc': 'Descarga la última versión y revoluciona tu flujo de desarrollo Python.',
        'cta_button': 'Descargar v3.2.7',
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
        'feature_projects_title': 'Project Management',
        'feature_projects_desc': 'Advanced build system with automatic script detection.',
        'feature_projects_item_1': 'Integration with <code>.gitignore</code>',
        'feature_projects_item_2': 'Automatic cleanup after build',
        'feature_projects_item_3': 'Dependency management',
        'feature_security_title': 'Code Protection',
        'feature_security_desc': 'Protect your intellectual property with advanced methods.',
        'feature_security_item_1': '<strong>Simple Blind:</strong> Package as <code>.iflappb</code>',
        'feature_security_item_2': '<strong>Super Blind:</strong> Class separation + encryption',
        'feature_build_title': 'Advanced Build',
        'feature_build_desc': 'Automatically detect candidate scripts, manage dependencies and minify your code.',
        'feature_build_item_1': '✓ built-in gitignore',
        'feature_build_item_2': '✓ automatic cleanup',
        'feature_build_item_3': '✓ lightweight packages',
        'feature_multiplatform_title': 'Multi-platform',
        'feature_multiplatform_desc': 'Generate executables for any platform from a single codebase.',
        'feature_apps_title': 'App Manager',
        'feature_apps_desc': 'Manage your local projects and installed apps.',
        'feature_config_title': 'Settings',
        'feature_config_desc': 'Full control over paths, language and customization.',
        'feature_moonfix_title': 'Deep Project Healing',
        'feature_moonfix_desc': 'Your ally to keep your projects healthy. Perform deep healing by scanning and repairing inconsistencies.',
        'feature_about_title': 'About Influent Package Maker',
        'feature_about_framework': 'Framework',
        'feature_about_framework_value': 'Qt 6.11.1',
        'feature_about_ui': 'UI System',
        'feature_about_ui_value': 'Leviathan',
        'feature_about_license': 'License',
        'feature_about_license_value': 'GNU GPL v3',
        'feature_about_developer': 'Developer',
        'feature_about_developer_value': 'Jesús Quijada',
        'feature_cli_title': 'Terminal (CLI)',
        'feature_cli_desc': 'Powerful command-line interface to automate tasks and integrate into CI/CD scripts.',
        'feature_news_title': 'What’s new in v3.2.7',
        'feature_news_item_1_title': 'Extended Editors',
        'feature_news_item_1_desc': 'Zed, Fleet, Emacs, Geany, Kate, Gedit',
        'feature_news_item_2_title': 'Linux Icons',
        'feature_news_item_2_desc': 'Improved rendering for Ubuntu',
        'feature_news_item_3_title': 'Fixes',
        'feature_news_item_3_desc': 'TypeError, white background, gradients',
        'cta_title': 'Ready for the next level?',
        'cta_desc': 'Download the latest version and revolutionize your Python development workflow.',
        'cta_button': 'Download v3.2.7',
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
        'feature_projects_title': 'Gestão de projetos',
        'feature_projects_desc': 'Sistema de compilação avançado com detecção automática de scripts.',
        'feature_projects_item_1': 'Integração com <code>.gitignore</code>',
        'feature_projects_item_2': 'Limpeza automática após a compilação',
        'feature_projects_item_3': 'Gestão de dependências',
        'feature_security_title': 'Proteção de código',
        'feature_security_desc': 'Proteja sua propriedade intelectual com métodos avançados.',
        'feature_security_item_1': '<strong>Simple Blind:</strong> empacote em <code>.iflappb</code>',
        'feature_security_item_2': '<strong>Super Blind:</strong> separação de classes + criptografia',
        'feature_build_title': 'Compilação avançada',
        'feature_build_desc': 'Detecte automaticamente scripts candidatos, gerencie dependências e minifique seu código.',
        'feature_build_item_1': '✓ gitignore integrado',
        'feature_build_item_2': '✓ limpeza automática',
        'feature_build_item_3': '✓ pacotes leves',
        'feature_multiplatform_title': 'Multi-plataforma',
        'feature_multiplatform_desc': 'Gere executáveis para qualquer plataforma a partir de um único código.',
        'feature_apps_title': 'Gerenciador de apps',
        'feature_apps_desc': 'Gerencie seus projetos locais e aplicativos instalados.',
        'feature_config_title': 'Configuração',
        'feature_config_desc': 'Controle total sobre caminhos, idioma e personalização.',
        'feature_moonfix_title': 'Cura profunda de projetos',
        'feature_moonfix_desc': 'Sua aliada para manter a saúde dos seus projetos. Faça uma cura profunda, escaneando e corrigindo inconsistências.',
        'feature_about_title': 'Sobre o Influent Package Maker',
        'feature_about_framework': 'Framework',
        'feature_about_framework_value': 'Qt 6.11.1',
        'feature_about_ui': 'Sistema de UI',
        'feature_about_ui_value': 'Leviathan',
        'feature_about_license': 'Licença',
        'feature_about_license_value': 'GNU GPL v3',
        'feature_about_developer': 'Desenvolvedor',
        'feature_about_developer_value': 'Jesús Quijada',
        'feature_cli_title': 'Terminal (CLI)',
        'feature_cli_desc': 'Interface poderosa de linha de comando para automatizar tarefas e integrar em scripts CI/CD.',
        'feature_news_title': 'Novidades v3.2.7',
        'feature_news_item_1_title': 'Editores estendidos',
        'feature_news_item_1_desc': 'Zed, Fleet, Emacs, Geany, Kate, Gedit',
        'feature_news_item_2_title': 'Ícones no Linux',
        'feature_news_item_2_desc': 'Renderização melhorada para Ubuntu',
        'feature_news_item_3_title': 'Correções',
        'feature_news_item_3_desc': 'TypeError, fundo branco, gradientes',
        'cta_title': 'Pronto para o próximo nível?',
        'cta_desc': 'Baixe a versão mais recente e revolucione seu fluxo de desenvolvimento em Python.',
        'cta_button': 'Baixar v3.2.7',
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
        'feature_projects_title': 'Gestion de projets',
        'feature_projects_desc': 'Système de compilation avancé avec détection automatique des scripts.',
        'feature_projects_item_1': 'Intégration avec <code>.gitignore</code>',
        'feature_projects_item_2': 'Nettoyage automatique après la compilation',
        'feature_projects_item_3': 'Gestion des dépendances',
        'feature_security_title': 'Protection du code',
        'feature_security_desc': 'Protégez votre propriété intellectuelle avec des méthodes avancées.',
        'feature_security_item_1': '<strong>Simple Blind:</strong> empaquetez en <code>.iflappb</code>',
        'feature_security_item_2': '<strong>Super Blind:</strong> séparation des classes + chiffrement',
        'feature_build_title': 'Compilation avancée',
        'feature_build_desc': 'Détectez automatiquement les scripts candidats, gérez les dépendances et minifiez votre code.',
        'feature_build_item_1': '✓ gitignore intégré',
        'feature_build_item_2': '✓ nettoyage automatique',
        'feature_build_item_3': '✓ paquets légers',
        'feature_multiplatform_title': 'Multi-plateforme',
        'feature_multiplatform_desc': 'Générez des exécutables pour n’importe quelle plateforme à partir d’un seul code.',
        'feature_apps_title': 'Gestionnaire d’apps',
        'feature_apps_desc': 'Gérez vos projets locaux et applications installées.',
        'feature_config_title': 'Configuration',
        'feature_config_desc': 'Contrôle total sur les chemins, la langue et la personnalisation.',
        'feature_moonfix_title': 'Guérison profonde des projets',
        'feature_moonfix_desc': 'Votre alliée pour maintenir la santé de vos projets. Effectuez une guérison profonde en scannant et en corrigeant les incohérences.',
        'feature_about_title': 'À propos d’Influent Package Maker',
        'feature_about_framework': 'Framework',
        'feature_about_framework_value': 'Qt 6.11.1',
        'feature_about_ui': 'Système UI',
        'feature_about_ui_value': 'Leviathan',
        'feature_about_license': 'Licence',
        'feature_about_license_value': 'GNU GPL v3',
        'feature_about_developer': 'Développeur',
        'feature_about_developer_value': 'Jesús Quijada',
        'feature_cli_title': 'Terminal (CLI)',
        'feature_cli_desc': 'Interface en ligne de commande puissante pour automatiser les tâches et s’intégrer aux scripts CI/CD.',
        'feature_news_title': 'Nouveautés v3.2.7',
        'feature_news_item_1_title': 'Éditeurs étendus',
        'feature_news_item_1_desc': 'Zed, Fleet, Emacs, Geany, Kate, Gedit',
        'feature_news_item_2_title': 'Icônes Linux',
        'feature_news_item_2_desc': 'Rendu amélioré pour Ubuntu',
        'feature_news_item_3_title': 'Corrections',
        'feature_news_item_3_desc': 'TypeError, fond blanc, dégradés',
        'cta_title': 'Prêt pour le niveau supérieur ?',
        'cta_desc': 'Téléchargez la dernière version et révolutionnez votre flux de développement Python.',
        'cta_button': 'Télécharger v3.2.7',
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
        'feature_projects_title': 'Projektmanagement',
        'feature_projects_desc': 'Erweitertes Build-System mit automatischer Skript-Erkennung.',
        'feature_projects_item_1': 'Integration mit <code>.gitignore</code>',
        'feature_projects_item_2': 'Automatische Bereinigung nach dem Build',
        'feature_projects_item_3': 'Abhängigkeitsverwaltung',
        'feature_security_title': 'Code-Schutz',
        'feature_security_desc': 'Schützen Sie Ihr geistiges Eigentum mit fortschrittlichen Methoden.',
        'feature_security_item_1': '<strong>Simple Blind:</strong> Verpacken Sie es als <code>.iflappb</code>',
        'feature_security_item_2': '<strong>Super Blind:</strong> Klassenaufteilung + Verschlüsselung',
        'feature_build_title': 'Erweiterter Build',
        'feature_build_desc': 'Erkennen Sie automatisch Kandidatenskripte, verwalten Sie Abhängigkeiten und minimieren Sie Ihren Code.',
        'feature_build_item_1': '✓ integriertes gitignore',
        'feature_build_item_2': '✓ automatische Bereinigung',
        'feature_build_item_3': '✓ leichte Pakete',
        'feature_multiplatform_title': 'Mehrplattformig',
        'feature_multiplatform_desc': 'Erzeugen Sie aus einem einzigen Codebase ausführbare Dateien für jede Plattform.',
        'feature_apps_title': 'App-Manager',
        'feature_apps_desc': 'Verwalten Sie Ihre lokalen Projekte und installierten Apps.',
        'feature_config_title': 'Einstellungen',
        'feature_config_desc': 'Volle Kontrolle über Pfade, Sprache und Anpassung.',
        'feature_moonfix_title': 'Tiefgehende Projektheilung',
        'feature_moonfix_desc': 'Ihr Verbündeter, um die Gesundheit Ihrer Projekte zu erhalten. Führen Sie eine tiefgehende Heilung durch, indem Sie Inkonsistenzen scannen und reparieren.',
        'feature_about_title': 'Über Influent Package Maker',
        'feature_about_framework': 'Framework',
        'feature_about_framework_value': 'Qt 6.11.1',
        'feature_about_ui': 'UI-System',
        'feature_about_ui_value': 'Leviathan',
        'feature_about_license': 'Lizenz',
        'feature_about_license_value': 'GNU GPL v3',
        'feature_about_developer': 'Entwickler',
        'feature_about_developer_value': 'Jesús Quijada',
        'feature_cli_title': 'Terminal (CLI)',
        'feature_cli_desc': 'Leistungsstarke Befehlszeilenschnittstelle zur Automatisierung von Aufgaben und Integration in CI/CD-Skripte.',
        'feature_news_title': 'Neuheiten in v3.2.7',
        'feature_news_item_1_title': 'Erweiterte Editoren',
        'feature_news_item_1_desc': 'Zed, Fleet, Emacs, Geany, Kate, Gedit',
        'feature_news_item_2_title': 'Linux-Symbole',
        'feature_news_item_2_desc': 'Verbesserte Darstellung für Ubuntu',
        'feature_news_item_3_title': 'Korrekturen',
        'feature_news_item_3_desc': 'TypeError, weißer Hintergrund, Verläufe',
        'cta_title': 'Bereit für die nächste Stufe?',
        'cta_desc': 'Laden Sie die neueste Version herunter und revolutionieren Sie Ihren Python-Entwicklungsworkflow.',
        'cta_button': 'Download v3.2.7',
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
        'feature_projects_title': 'Gestione dei progetti',
        'feature_projects_desc': 'Sistema di build avanzato con rilevamento automatico degli script.',
        'feature_projects_item_1': 'Integrazione con <code>.gitignore</code>',
        'feature_projects_item_2': 'Pulizia automatica dopo la build',
        'feature_projects_item_3': 'Gestione delle dipendenze',
        'feature_security_title': 'Protezione del codice',
        'feature_security_desc': 'Proteggi la tua proprietà intellettuale con metodi avanzati.',
        'feature_security_item_1': '<strong>Simple Blind:</strong> pacchetta come <code>.iflappb</code>',
        'feature_security_item_2': '<strong>Super Blind:</strong> separazione delle classi + crittografia',
        'feature_build_title': 'Build avanzata',
        'feature_build_desc': 'Rileva automaticamente gli script candidati, gestisce le dipendenze e minimizza il tuo codice.',
        'feature_build_item_1': '✓ gitignore integrato',
        'feature_build_item_2': '✓ pulizia automatica',
        'feature_build_item_3': '✓ pacchetti leggeri',
        'feature_multiplatform_title': 'Multipiattaforma',
        'feature_multiplatform_desc': 'Genera eseguibili per qualsiasi piattaforma da un singolo codice.',
        'feature_apps_title': 'Gestore app',
        'feature_apps_desc': 'Gestisci i tuoi progetti locali e le app installate.',
        'feature_config_title': 'Impostazioni',
        'feature_config_desc': 'Controllo totale su percorsi, lingua e personalizzazione.',
        'feature_moonfix_title': 'Guarigione profonda dei progetti',
        'feature_moonfix_desc': 'La tua alleata per mantenere sani i tuoi progetti. Esegui una guarigione profonda scansionando e riparando le incongruenze.',
        'feature_about_title': 'Informazioni su Influent Package Maker',
        'feature_about_framework': 'Framework',
        'feature_about_framework_value': 'Qt 6.11.1',
        'feature_about_ui': 'Sistema UI',
        'feature_about_ui_value': 'Leviathan',
        'feature_about_license': 'Licenza',
        'feature_about_license_value': 'GNU GPL v3',
        'feature_about_developer': 'Sviluppatore',
        'feature_about_developer_value': 'Jesús Quijada',
        'feature_cli_title': 'Terminale (CLI)',
        'feature_cli_desc': 'Potente interfaccia a riga di comando per automatizzare attività e integrarsi con script CI/CD.',
        'feature_news_title': 'Novità v3.2.7',
        'feature_news_item_1_title': 'Editor estesi',
        'feature_news_item_1_desc': 'Zed, Fleet, Emacs, Geany, Kate, Gedit',
        'feature_news_item_2_title': 'Icone Linux',
        'feature_news_item_2_desc': 'Rendering migliorato per Ubuntu',
        'feature_news_item_3_title': 'Correzioni',
        'feature_news_item_3_desc': 'TypeError, sfondo bianco, gradienti',
        'cta_title': 'Pronto per il livello successivo?',
        'cta_desc': 'Scarica l’ultima versione e rivoluziona il tuo flusso di sviluppo Python.',
        'cta_button': 'Scarica v3.2.7',
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
        'feature_projects_title': 'プロジェクト管理',
        'feature_projects_desc': 'スクリプトを自動検出する高度なビルドシステム。',
        'feature_projects_item_1': '<code>.gitignore</code> と統合',
        'feature_projects_item_2': 'ビルド後の自動クリーンアップ',
        'feature_projects_item_3': '依存関係管理',
        'feature_security_title': 'コード保護',
        'feature_security_desc': '高度な手法で知的財産を保護します。',
        'feature_security_item_1': '<strong>Simple Blind:</strong> <code>.iflappb</code> としてパッケージ化',
        'feature_security_item_2': '<strong>Super Blind:</strong> クラス分離 + 暗号化',
        'feature_build_title': '高度なビルド',
        'feature_build_desc': '候補スクリプトを自動検出し、依存関係を管理してコードを最小化します。',
        'feature_build_item_1': '✓ 組み込み gitignore',
        'feature_build_item_2': '✓ 自動クリーンアップ',
        'feature_build_item_3': '✓ 軽量パッケージ',
        'feature_multiplatform_title': 'マルチプラットフォーム',
        'feature_multiplatform_desc': '単一コードベースからあらゆるプラットフォーム向けの実行ファイルを生成します。',
        'feature_apps_title': 'アプリマネージャー',
        'feature_apps_desc': 'ローカルプロジェクトとインストール済みアプリを管理します。',
        'feature_config_title': '設定',
        'feature_config_desc': 'パス、言語、カスタマイズの完全な制御。',
        'feature_moonfix_title': 'プロジェクトの深層修復',
        'feature_moonfix_desc': 'プロジェクトの健全性を保つための味方です。整合性をスキャンして修復し、深層修復を実行します。',
        'feature_about_title': 'Influent Package Maker について',
        'feature_about_framework': 'フレームワーク',
        'feature_about_framework_value': 'Qt 6.11.1',
        'feature_about_ui': 'UI システム',
        'feature_about_ui_value': 'Leviathan',
        'feature_about_license': 'ライセンス',
        'feature_about_license_value': 'GNU GPL v3',
        'feature_about_developer': '開発者',
        'feature_about_developer_value': 'Jesús Quijada',
        'feature_cli_title': 'ターミナル (CLI)',
        'feature_cli_desc': 'タスクを自動化し、CI/CD スクリプトに統合するための強力なコマンドラインインターフェース。',
        'feature_news_title': 'v3.2.7 の新機能',
        'feature_news_item_1_title': '拡張エディタ',
        'feature_news_item_1_desc': 'Zed, Fleet, Emacs, Geany, Kate, Gedit',
        'feature_news_item_2_title': 'Linux アイコン',
        'feature_news_item_2_desc': 'Ubuntu の描画を改善',
        'feature_news_item_3_title': '修正点',
        'feature_news_item_3_desc': 'TypeError、白背景、グラデーション',
        'cta_title': '次のレベルへ進みますか？',
        'cta_desc': '最新バージョンをダウンロードして、Python 開発ワークフローを一新しましょう。',
        'cta_button': 'v3.2.7 をダウンロード',
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
        'feature_projects_title': '项目管理',
        'feature_projects_desc': '具有自动脚本检测的高级构建系统。',
        'feature_projects_item_1': '与 <code>.gitignore</code> 集成',
        'feature_projects_item_2': '构建后自动清理',
        'feature_projects_item_3': '依赖管理',
        'feature_security_title': '代码保护',
        'feature_security_desc': '使用高级方法保护您的知识产权。',
        'feature_security_item_1': '<strong>Simple Blind:</strong> 打包为 <code>.iflappb</code>',
        'feature_security_item_2': '<strong>Super Blind:</strong> 类分离 + 加密',
        'feature_build_title': '高级构建',
        'feature_build_desc': '自动检测候选脚本、管理依赖并精简您的代码。',
        'feature_build_item_1': '✓ 内置 gitignore',
        'feature_build_item_2': '✓ 自动清理',
        'feature_build_item_3': '✓ 轻量包',
        'feature_multiplatform_title': '多平台',
        'feature_multiplatform_desc': '从单一代码库生成适用于任何平台的可执行文件。',
        'feature_apps_title': '应用管理器',
        'feature_apps_desc': '管理您的本地项目和已安装应用。',
        'feature_config_title': '设置',
        'feature_config_desc': '完全控制路径、语言和自定义。',
        'feature_moonfix_title': '深度修复项目',
        'feature_moonfix_desc': '帮助您保持项目健康的伙伴。通过扫描并修复不一致之处来执行深度修复。',
        'feature_about_title': '关于 Influent Package Maker',
        'feature_about_framework': '框架',
        'feature_about_framework_value': 'Qt 6.11.1',
        'feature_about_ui': 'UI 系统',
        'feature_about_ui_value': 'Leviathan',
        'feature_about_license': '许可证',
        'feature_about_license_value': 'GNU GPL v3',
        'feature_about_developer': '开发者',
        'feature_about_developer_value': 'Jesús Quijada',
        'feature_cli_title': '终端 (CLI)',
        'feature_cli_desc': '强大的命令行界面，可自动化任务并与 CI/CD 脚本集成。',
        'feature_news_title': 'v3.2.7 新内容',
        'feature_news_item_1_title': '扩展编辑器',
        'feature_news_item_1_desc': 'Zed, Fleet, Emacs, Geany, Kate, Gedit',
        'feature_news_item_2_title': 'Linux 图标',
        'feature_news_item_2_desc': '增强 Ubuntu 的渲染效果',
        'feature_news_item_3_title': '修复',
        'feature_news_item_3_desc': 'TypeError、白色背景、渐变',
        'cta_title': '准备好进入下一个层级了吗？',
        'cta_desc': '下载最新版本，彻底改变您的 Python 开发流程。',
        'cta_button': '下载 v3.2.7',
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
    # Table to map Telegram chat ids and usernames when users register the bot
    c.execute('''CREATE TABLE IF NOT EXISTS telegram_users
                 (chat_id INTEGER PRIMARY KEY,
                  username TEXT,
                  registered_at DATETIME)''')

    # Reports submitted from the website
    c.execute('''CREATE TABLE IF NOT EXISTS reports
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ticket TEXT,
                  title TEXT,
                  description TEXT,
                  reporter_username TEXT,
                  reporter_telegram_id TEXT,
                  reporter_chat_id INTEGER,
                  reporter_ip TEXT,
                  resolved INTEGER DEFAULT 0,
                  resolution_note TEXT,
                  resolved_at DATETIME,
                  created_at DATETIME)''')
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


    # --- Telegram integration helpers and routes ---
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_OWNER_ID = os.getenv('TELEGRAM_OWNER_ID')

    def send_telegram_message(chat_id, text, parse_mode='HTML'):
        if not TELEGRAM_BOT_TOKEN:
            print('Telegram token not configured; skipping send')
            return None
        api = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        payload = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode}
        try:
            resp = requests.post(api, json=payload, timeout=8)
            return resp.json() if resp.status_code == 200 else None
        except Exception as e:
            print(f'Error sending telegram message: {e}')
            return None


    @app.route('/report', methods=['GET', 'POST'])
    def report_issue():
        if request.method == 'GET':
            return render_template('report.html')

        # POST: create report and notify owner via Telegram
        title = request.form.get('title')
        description = request.form.get('description')
        reporter_username = request.form.get('reporter_username')
        reporter_telegram_id = request.form.get('reporter_telegram_id') or None

        ticket = f"R-{uuid.uuid4().hex[:8]}"
        created_at = datetime.now()

        reporter_chat_id = None
        reporter_ip = request.remote_addr
        # If user provided a numeric telegram id, use it as chat id
        try:
            if reporter_telegram_id:
                reporter_chat_id = int(reporter_telegram_id)
        except Exception:
            reporter_chat_id = None

        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO reports (ticket, title, description, reporter_username, reporter_telegram_id, reporter_chat_id, reporter_ip, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                  (ticket, title, description, reporter_username, reporter_telegram_id, reporter_chat_id, reporter_ip, created_at))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f'Error saving report: {e}')

        # Notify owner
        owner_text = f"<b>REPORT {ticket}</b>\n\n" + \
                     f"<b>Título:</b> {title}\n" + \
                     f"<b>Descripción:</b> {description}\n\n" + \
                     f"<b>Reporter:</b> {reporter_username or 'N/A'}\n" + \
                     f"<b>Telegram ID (if provided):</b> {reporter_telegram_id or 'N/A'}\n\n" + \
                     "Responde a este mensaje para enviar un mensaje al reporter (si está registrado)."

        if TELEGRAM_OWNER_ID:
            try:
                send_telegram_message(TELEGRAM_OWNER_ID, owner_text)
            except Exception as e:
                print(f'Error notifying owner: {e}')

        return render_template('report.html', submitted=True, ticket=ticket)


    @app.route('/api/telegram_webhook', methods=['POST'])
    def telegram_webhook():
        data = request.json or {}
        try:
            message = data.get('message') or data.get('edited_message')
            if not message:
                return jsonify({'ok': True})

            from_user = message.get('from', {})
            text = message.get('text', '')
            chat = message.get('chat', {})
            chat_id = chat.get('id')
            username = from_user.get('username')
            user_id = from_user.get('id')

            # If a user registers the bot, store mapping
            if text and text.strip().lower().startswith('/register'):
                try:
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute('REPLACE INTO telegram_users (chat_id, username, registered_at) VALUES (?, ?, ?)', (chat_id, username, datetime.now()))
                    conn.commit()
                    conn.close()
                    send_telegram_message(chat_id, 'Registro completado. Ahora podrás recibir mensajes de soporte a través de este bot.')
                except Exception as e:
                    print(f'Error saving telegram user: {e}')
                return jsonify({'ok': True})

            # If owner replied to a report message, forward the reply to the reporter
            if str(user_id) == str(TELEGRAM_OWNER_ID) and message.get('reply_to_message'):
                reply_to = message.get('reply_to_message')
                # Look for REPORT ticket in the replied-to text
                replied_text = reply_to.get('text', '')
                import re
                m = re.search(r'REPORT\s+(R-[0-9a-fA-F]+)', replied_text)
                if m:
                    ticket = m.group(1)
                    # Find report and reporter chat id
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute('SELECT reporter_chat_id, reporter_username FROM reports WHERE ticket = ?', (ticket,))
                    row = c.fetchone()
                    conn.close()
                    if row:
                        reporter_chat_id, reporter_username = row
                        if reporter_chat_id:
                            # forward owner's text to reporter
                            send_telegram_message(reporter_chat_id, f"Respuesta del Owner sobre {ticket}:\n\n{text}")
                            send_telegram_message(TELEGRAM_OWNER_ID, f"Mensaje enviado a {reporter_username or reporter_chat_id}.")
                        else:
                            send_telegram_message(TELEGRAM_OWNER_ID, f"El reporter de {ticket} no está registrado o no proporcionó chat id.")
                    else:
                        send_telegram_message(TELEGRAM_OWNER_ID, f"No se encontró el ticket {ticket}.")

            return jsonify({'ok': True})
        except Exception as e:
            print(f'Error in telegram_webhook: {e}')
            return jsonify({'ok': False, 'error': str(e)}), 500


    def try_notify_via_ip(ip, payload):
        """Attempt simple HTTP callbacks to the reporter IP to notify of resolution."""
        if not ip:
            return False, 'no ip'
        urls = [
            f'http://{ip}/pm/notify',
            f'http://{ip}:9000/pm/notify',
            f'http://{ip}/notify',
            f'http://{ip}:9000/notify'
        ]
        headers = {'Content-Type': 'application/json'}
        for u in urls:
            try:
                resp = requests.post(u, json=payload, headers=headers, timeout=3)
                if resp.status_code < 400:
                    return True, f'ok {u} {resp.status_code}'
            except Exception as e:
                # continue trying other endpoints
                last_err = str(e)
        return False, last_err if 'last_err' in locals() else 'failed'


    @app.route('/admin/reports')
    def admin_reports():
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT ticket, title, description, reporter_username, reporter_telegram_id, reporter_chat_id, reporter_ip, resolved, resolution_note, resolved_at, created_at FROM reports ORDER BY created_at DESC')
            rows = c.fetchall()
            conn.close()
            reports = []
            for r in rows:
                reports.append({
                    'ticket': r[0], 'title': r[1], 'description': r[2], 'reporter_username': r[3], 'reporter_telegram_id': r[4], 'reporter_chat_id': r[5], 'reporter_ip': r[6], 'resolved': bool(r[7]), 'resolution_note': r[8], 'resolved_at': r[9], 'created_at': r[10]
                })
            return render_template('admin_reports.html', reports=reports)
        except Exception as e:
            print(f'Error loading admin reports: {e}')
            return render_template('error.html', code=500, message='Error cargando reports'), 500


    @app.route('/admin/report/<ticket>/resolve', methods=['POST'])
    def resolve_report(ticket):
        note = request.form.get('resolution_note') or 'Resuelto'
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT reporter_chat_id, reporter_ip FROM reports WHERE ticket = ?', (ticket,))
            row = c.fetchone()
            if not row:
                conn.close()
                return render_template('error.html', code=404, message='Ticket no encontrado'), 404
            reporter_chat_id, reporter_ip = row
            now = datetime.now()
            c.execute('UPDATE reports SET resolved = 1, resolution_note = ?, resolved_at = ? WHERE ticket = ?', (note, now, ticket))
            conn.commit()
            conn.close()

            notified = False
            notify_log = ''
            # Try Telegram first
            if reporter_chat_id:
                res = send_telegram_message(reporter_chat_id, f"Tu reporte {ticket} ha sido resuelto:\n\n{note}")
                notified = bool(res)
                notify_log = f'tg:{res}'
            else:
                payload = {'ticket': ticket, 'status': 'resolved', 'note': note}
                ok, info = try_notify_via_ip(reporter_ip, payload)
                notified = ok
                notify_log = info

            # Inform owner about result
            owner_msg = f"Reporte {ticket} marcado como resuelto. Notificado: {notified}. Info: {notify_log}"
            if TELEGRAM_OWNER_ID:
                send_telegram_message(TELEGRAM_OWNER_ID, owner_msg)

            return ('', 204) if request.headers.get('Accept') == 'application/json' else ('', 204)
        except Exception as e:
            print(f'Error resolving report: {e}')
            return render_template('error.html', code=500, message='Error al resolver report'), 500

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
