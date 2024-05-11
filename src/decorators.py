from functools import wraps
from flask import request, jsonify
import jwt
import os
from .database import connector
from .database.load_env import LoadDBEnv
from dotenv import load_dotenv
from .database.blacklist_token import BlackListToken
load_dotenv()

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        blacklist_token = BlackListToken(db)

        token = request.headers.get("Authorization")
        
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        
        if blacklist_token.is_token_blacklisted(token.split()[1]):
            return jsonify({"message": "Token is blacklisted"}), 401
        try:
            secret_key = os.environ.get("JWT_SECRET_KEY")
            payload = jwt.decode(token.split()[1], secret_key, algorithms=["HS256"])
         
            request.jwt_payload = payload 
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated_function

def multiple_tokens_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        blacklist_token = BlackListToken(db)

        tokens = []
        # Extract tokens from Authorization headers
        authorization_headers = request.headers.get_all("Authorization")
        if not authorization_headers:
            return jsonify({"message": "Token is missing"}), 401
        if authorization_headers:
            token_strings = authorization_headers[0].split(",")
            for token_string in token_strings:
                # Extract token from "Bearer <token>" format
                token = token_string.strip().split()[1]  
                tokens.append(token)
        try:
            secret_key = os.environ.get("JWT_SECRET_KEY")
            payloads = []
            # Decode each token and store the payload
            for token in tokens:
                if blacklist_token.is_token_blacklisted(token):
                    return jsonify({"message": "One or more tokens are blacklisted"}), 401
                payload = jwt.decode(token, secret_key, algorithms=["HS256"])
                payloads.append(payload)
           
            request.jwt_payloads = payloads  # Store payloads in request object
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "One or more tokens have expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "One or more tokens are invalid"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def multiple_tokens_logout(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        tokens = []
        # Extract tokens from Authorization headers
        authorization_headers = request.headers.get_all("Authorization")
        if not authorization_headers:
            return jsonify({"message": "Token is missing"}), 401
        if authorization_headers:
            token_strings = authorization_headers[0].split(",")
            for token_string in token_strings:
                # Extract token from "Bearer <token>" format
                token = token_string.strip().split()[1]  
                tokens.append(token)
        try:
            request.jwt_payloads = tokens  # Store payloads in request object
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "One or more tokens have expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "One or more tokens are invalid"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function