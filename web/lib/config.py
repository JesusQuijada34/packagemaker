# -*- coding: utf-8 -*-
"""
Configuration module for Package Maker Web
No persistent disks required - uses temp directories
"""

import os
import tempfile

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
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload
    ALLOWED_EXTENSIONS = {'zip', 'iflapp'}
    
    # Repo root (parent of web/)
    REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Temp directories (no persistent disks needed)
    TEMP_DIR = tempfile.gettempdir()
    
    # Server settings
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}