from flask import Blueprint, request, jsonify
from ..database import connector
from ..database.manager_auth import Auth
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
    
@manager_bp.route("/delete_user", methods=["DELETE"])
@token_required
def delete_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    
    username = request.jwt_payload.get("manager_username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    username_delete = data.get("username", None)
    if not username_delete:
        return jsonify({"error": "Username not provided"}), 400
    
    deleted = auth.delete_user(username_delete)
    if deleted:
        return jsonify({"message": f"User '{username_delete}' deleted successfully"}), 200
    else:
        return jsonify({"error": f"Failed to delete user '{username_delete}'"}), 500

@manager_bp.route("/change_user_status", methods=["PATCH"])
@token_required
def change_user_status():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    
    username = request.jwt_payload.get("manager_username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    username_change = data.get("username", None)
    new_status = data.get("new_status", None)
    if not username_change or not new_status:
        return jsonify({"error": "Username and status not provided"}), 400
   
    changed = auth.change_user_status(username_change, new_status)
    if changed:
        return jsonify({"message": f"User '{username_change}' status changed to '{new_status}'"}), 200
    else:
        return jsonify({"error": f"Failed to change status of user '{username_change}'"}), 500

