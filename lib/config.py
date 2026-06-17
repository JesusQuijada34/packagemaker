# -*- coding: utf-8 -*-
import os
import tempfile

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'pm-secret-key')
    JWT_SECRET = os.environ.get('JWT_SECRET', 'pm-jwt-secret')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
    GITHUB_REPO = os.environ.get('GITHUB_REPO', 'JesusQuijada34/packagemaker')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
    TEMP_DIR = tempfile.gettempdir()
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

config = {'default': Config, 'development': Config, 'production': Config}
