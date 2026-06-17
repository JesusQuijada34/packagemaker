# -*- coding: utf-8 -*-
import jwt
from datetime import datetime, timedelta

def create_token(data, secret, expires_in=3600):
    payload = {**data, 'exp': datetime.utcnow() + timedelta(seconds=expires_in), 'iat': datetime.utcnow()}
    return jwt.encode(payload, secret, algorithm='HS256')

def verify_token(token, secret):
    try:
        return jwt.decode(token, secret, algorithms=['HS256'])
    except:
        return None