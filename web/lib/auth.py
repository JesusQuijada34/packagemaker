# -*- coding: utf-8 -*-
"""
Authentication module with JWT support
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, redirect, url_for


def create_token(data, secret, algorithm='HS256', expires_in=3600):
    """Create JWT token"""
    payload = {
        **data,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def verify_token(token, secret, algorithm='HS256'):
    """Verify JWT token"""
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """Decorator for routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app
        token = request.cookies.get('auth_token')
        
        if not token:
            return redirect(url_for('login'))
        
        secret = current_app.config.get('JWT_SECRET', 'packagemaker-jwt-secret')
        user = verify_token(token, secret)
        
        if not user:
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """Decorator for API routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = request.cookies.get('auth_token')
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        secret = current_app.config.get('JWT_SECRET', 'packagemaker-jwt-secret')
        user = verify_token(token, secret)
        
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return f(*args, **kwargs)
    return decorated_function