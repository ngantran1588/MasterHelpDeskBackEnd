from flask import Blueprint, request, jsonify
from ..database import connector
from ..database.auth import Auth
from ..database.load_env import LoadDBEnv
import os
from dotenv import load_dotenv
from ..decorators import token_required
from datetime import datetime, timedelta, timezone
import jwt

load_dotenv()

manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/login', methods=['POST'])
def login():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    manager_username = data['manager_username']
    manager_password = data['manager_password']

    if auth.login(manager_username, manager_password):
        payload = {"manager_username": manager_username, "exp": datetime.now(timezone.utc) + timedelta(minutes=10)}
        token = jwt.encode(payload, os.environ.get("JWT_SECRET_KEY"), algorithm="HS256")
        db.close()
        return jsonify({"message": "Login successful", "access_token": token}), 200
    else:
        db.close()
        return jsonify({'message': 'Invalid credentials'}), 401


@manager_bp.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful"})
    response.delete_cookie("access_token")
    return response, 200
    