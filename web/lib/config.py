# -*- coding: utf-8 -*-
"""
Configuration module for Package Maker Web
"""

import os

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'packagemaker-secret-key-dev')
    JWT_SECRET = os.environ.get('JWT_SECRET', 'packagemaker-jwt-secret')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRES_IN = 3600  # 1 hour
    
    # GitHub settings
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
    GITHUB_REPO = os.environ.get('GITHUB_REPO', 'JesusQuijada34/packagemaker')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'zip', 'iflapp'}
    
    # Paths (relative to web/)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    PROJECTS_FOLDER = os.path.join(BASE_DIR, 'projects')
    RELEASES_FOLDER = os.path.join(BASE_DIR, 'releases')
    
    # Server settings
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Ensure directories exist
    for _dir in [UPLOAD_FOLDER, PROJECTS_FOLDER, RELEASES_FOLDER]:
        os.makedirs(_dir, exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}