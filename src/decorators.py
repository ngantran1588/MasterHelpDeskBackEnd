from functools import wraps
from flask import request, jsonify
import jwt
import os
from dotenv import load_dotenv
load_dotenv()


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        
        if not token:
            return jsonify({"message": "Token is missing"}), 401
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
