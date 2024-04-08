from flask import Blueprint, request, jsonify
from ..database import connector
from ..database.auth import Auth
from ..database.load_env import LoadDBEnv
from datetime import datetime, timedelta, timezone
import jwt
import os
from dotenv import load_dotenv
from ..decorators import token_required

load_dotenv()

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not all([username, password]) or username == '' or password == '':
        return jsonify({"message": "Missing required fields"}), 400
   
    if auth.login(username, password):
        payload = {"username": username, "exp": datetime.now(timezone.utc) + timedelta(minutes=10)}
        token = jwt.encode(payload, os.environ.get("JWT_SECRET_KEY"), algorithm="HS256")
        db.close()
        return jsonify({"message": "Login successful", "access_token": token}), 200
    else:
        db.close()
        return jsonify({"message": "Invalid credentials"}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful"})
    response.delete_cookie("access_token")
    return response, 200

@auth_bp.route("/signup", methods=["POST"])
def sign_up():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    full_name = data["full_name"]
    email = data["email"]

    if auth.sign_up(username, password, full_name, email):
        db.close()
        return jsonify({"message": "Sign-up successful"}), 201
    else:
        db.close()
        return jsonify({"message": "Sign-up failed"}), 400


@auth_bp.route("/forgot_password", methods=["POST"])
def forgot_password():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]

    if auth.send_otp(email):
        db.close()
        return jsonify({"message": "OTP sent successfully"}), 200
    else:
        db.close()
        return jsonify({"message": "Failed to send OTP"}), 500

@auth_bp.route("/resend_otp", methods=["POST"])
def resend_otp():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]

    auth.delete_used_otp(email)

    if auth.send_otp(email):
        db.close()
        return jsonify({"message": "OTP sent successfully"}), 200
    else:
        db.close()
        return jsonify({"message": "Failed to send OTP"}), 500
    

@auth_bp.route("/verify_otp", methods=["POST"])
@token_required
def verify_otp():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]
    otp = data["otp"]

    if auth.verify_otp(email, otp):
        payload = {"otp_verified": True, "exp": datetime.now() + timedelta(minutes=10)}
        token = jwt.encode(payload, os.environ.get("JWT_SECRET_KEY"), algorithm="HS256")
        auth.delete_used_otp(email, otp)
        db.close()
        return jsonify({"message": "OTP verified successfully", "otp_verified": token}), 200
    else:
        auth.delete_expired_otp()
        db.close()
        return jsonify({"message": "OTP verification failed"}), 500
    
@auth_bp.route("/change_password", methods=["POST"])
@token_required
def change_password():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    username = data["username"]
    old_password = data["old_password"]
    new_password = data["new_password"]

    otp_verified = request.jwt_payload.get("otp_verified")
    if otp_verified != True:
        db.close()
        return jsonify({"message": "Verify OTP first"}), 403
    username_token = request.jwt_payload.get("username")
    if username != username_token:
        db.close()
        return jsonify({"message": "You don't have permission"}), 403 
    
    message, status = auth.change_password(username, new_password, old_password)

    response = jsonify({"message": message})
    response.delete_cookie("otp_verified")  # Remove token cookie
    
    db.close()
    if status:
        return response, 200
    else:
        return response, 500
    
@auth_bp.route("/reset_password", methods=["POST"])
@token_required
def reset_password():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    username = data["username"]
    new_password = data["new_password"]

    otp_verified = request.jwt_payload.get("otp_verified")
    if otp_verified != True:
        db.close()
        return jsonify({"message": "Verify OTP first"}), 403
    username_token = request.jwt_payload.get("username")
    if username != username_token:
        db.close()
        return jsonify({"message": "You don't have permission"}), 403 
    
    message, status = auth.reset_password(username, new_password)

    response = jsonify({"message": message})
    response.delete_cookie("otp_verified")  # Remove token cookie
    
    db.close()
    if status:
        return response, 200
    else:
        return response, 500
@auth_bp.route("/change_role_to_superuser", methods=["POST"])
@token_required
def change_role_to_superuser():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    username = request.jwt_payload.get("username")
    
    message, status = auth.change_role_to_superuser(username)

    if status:
        db.close()
        return jsonify({"message": message}), 200
    else:
        db.close()
        return jsonify({"message": message}), 500
    
@auth_bp.route("/change_role_to_user", methods=["POST"])
@token_required
def change_role_to_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    username = request.jwt_payload.get("username")
    
    message, status = auth.change_role_to_user(username)

    if status:
        db.close()
        return jsonify({"message": message}), 200
    else:
        db.close()
        return jsonify({"message": message}), 500
    
@auth_bp.route("/change_role", methods=["POST"])
@token_required
def change_role():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    username = request.jwt_payload.get("username")
    role_id = data["role_id"]

    message, status = auth.change_role(username, role_id)

    if status:
        db.close()
        return jsonify({"message": message}), 200
    else:
        db.close()
        return jsonify({"message": message}), 500

@auth_bp.route("/check_pass", methods=["POST"])
@token_required
def check_pass():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    username = request.jwt_payload.get("username")
    input_pass = data["password"]

    status = auth.check_user_pass(username, input_pass)

    if status:
        db.close()
        return jsonify({"message": "Success"}), 200
    else:
        db.close()
        return jsonify({"message": "Unauthorized"}), 403