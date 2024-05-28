from flask import Blueprint, request, jsonify
from ..database import connector
from ..database.auth import Auth
from ..database.role import Role
from ..database.load_env import LoadDBEnv
from ..database.blacklist_token import BlackListToken
from datetime import datetime, timedelta, timezone
import jwt
import os
from dotenv import load_dotenv
from ..decorators import token_required, multiple_tokens_required, multiple_tokens_logout

load_dotenv()

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)
    role = Role(db)
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not all([username, password]) or username == '' or password == '':
        return jsonify({"message": "Missing required fields"}), 400
    
    if not auth.exist_username(username):
        return jsonify({"message": "Your account is not exist"}), 401
    
    if auth.is_inactive_user(username):
        return jsonify({"message": "Your account is inactive"}), 401

    if auth.login(username, password):
        payload = {"username": username, "exp": datetime.now(timezone.utc) + timedelta(minutes=45)}
        token = jwt.encode(payload, os.environ.get("JWT_SECRET_KEY"), algorithm="HS256")
        role_id = auth.get_role_by_username(username)
        list_role = []
        for e in role_id:
            role_name = role.get_role_name_by_id(e)
            if role_name == None:
                return jsonify({"message": "Error in querying role"}), 500
            list_role.append(role_name)
        db.close()
        return jsonify({"message": "Login successful", "access_token": token, "role": role}), 200
    else:
        db.close()
        return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route("/logout", methods=["POST"])
@multiple_tokens_logout
def logout():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    blacklist_token = BlackListToken(db)
    response = jsonify({"message": "Logout successful"})
    response.delete_cookie("access_token")

    for payload in request.jwt_payloads:
        msg, status = blacklist_token.add_to_blacklist(payload)
        if status == 500:
            return msg, status
    
    msg, status = blacklist_token.remove_expired_tokens()
    db.close()
    return msg, status

@auth_bp.route("/signup", methods=["POST"])
def sign_up():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]
    username = data["username"]

    if auth.exist_username(username):
        db.close()
        return jsonify({"message": "Email existed"}), 500      

    if auth.exist_email(email):
        db.close()
        return jsonify({"message": "Email existed"}), 500      
    
    if auth.send_otp(email):
        db.close()
        return jsonify({"message": "Send OTP successfully"}), 200
    else:
        db.close()
        return jsonify({"message": "Failed to send OTP"}), 500

@auth_bp.route("/verify_identity", methods=["POST"])
def verify_identity():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]
    otp = data["otp"]
    username = data["username"]
    password = data["password"]
    full_name = data["full_name"] 

    if auth.verify_otp(email, otp):
        auth.delete_used_otp(email, otp)
        result, msg = auth.sign_up(username, password, full_name, email)
        if result:
            db.close()
            return jsonify({"message": msg}), 201
        else:
            db.close()
            return jsonify({"message": msg}), 400
    else:
        auth.delete_expired_otp()
        db.close()
        return jsonify({"message": "Identity failed"}), 500
    
@auth_bp.route("/forgot_password", methods=["POST"])
def forgot_password():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]

    if not auth.exist_email(email):
        db.close()
        return jsonify({"message": "Email does not exist"}), 404

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
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]

    auth.delete_otp_email(email)

    if not auth.exist_email(email):
        db.close()
        return jsonify({"message": "Email does not exist"}), 404

    if auth.send_otp(email):
        db.close()
        return jsonify({"message": "OTP sent successfully"}), 200
    else:
        db.close()
        return jsonify({"message": "Failed to send OTP"}), 500
    
@auth_bp.route("/verify_otp", methods=["POST"])
def verify_otp():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]
    otp = data["otp"]

    if auth.verify_otp(email, otp):
        payload = {"otp_verified": True, "exp": datetime.now(timezone.utc) + timedelta(minutes=10)}
        token = jwt.encode(payload, os.environ.get("JWT_SECRET_KEY"), algorithm="HS256")
        auth.delete_used_otp(email, otp)
        db.close()
        return jsonify({"message": "OTP verified successfully", "otp_verified": token}), 200
    else:
        auth.delete_expired_otp()
        db.close()
        return jsonify({"message": "OTP verification failed"}), 500
    
@auth_bp.route("/change_password", methods=["POST"])
@multiple_tokens_required
def change_password():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    username = data["username"]
    old_password = data["old_password"]
    new_password = data["new_password"]
    
    otp_verified = None
    username_token = None
    for payload in request.jwt_payloads:
        if payload.get("otp_verified"):
            otp_verified = payload["otp_verified"]
        if payload.get("username"):
            username_token = payload["username"]
    
    if otp_verified != True:
        db.close()
        return jsonify({"message": "Verify OTP first"}), 403
    
    if username != username_token:
        db.close()
        return jsonify({"message": "You don't have permission"}), 403 
    
    if old_password == new_password:
        return jsonify({"message": "New password can't be the same as old password"}), 400

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
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]
    new_password = data["new_password"]

    otp_verified = request.jwt_payload.get("otp_verified")
    if otp_verified != True:
        db.close()
        return jsonify({"message": "Verify OTP first"}), 403
    
    message, status = auth.reset_password(email, new_password)

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
    db.connect()
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
    db.connect()
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
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    role_id = data["role_id"]
    username_change = data["username"]

    message, status = auth.change_role(username_change, role_id)

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
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    input_pass = data["password"]

    status = auth.check_user_pass(username, input_pass)

    if status:
        db.close()
        return jsonify({"message": "Success"}), 200
    else:
        db.close()
        return jsonify({"message": "Unauthorized"}), 403

@auth_bp.route("/update_information", methods=["PUT"])
@token_required
def update_information():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)
    data = request.get_json()
    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    full_name = data.get("full_name")
    email = data.get("email")

    status = auth.update_information(username, full_name, email)

    if status:
        db.close()
        return jsonify({"message": "Success"}), 200
    else:
        db.close()
        return jsonify({"message": "Unauthorized"}), 403

@auth_bp.route("/get_profile", methods=["GET"])
@token_required
def get_profile():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)
    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    customer = auth.get_profile(username)
    
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if customer:
        db.close()
        return jsonify(customer), 200
    else:
        db.close()
        return jsonify({"message": "Unauthorized"}), 403
    
@auth_bp.route("/get_all_profile", methods=["GET"])
@token_required
def get_all_profile():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)
    
    username = request.jwt_payload.get("manager_username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    customers = auth.get_all_profile()

    if customers:
        db.close()
        return jsonify(customers), 200
    else:
        db.close()
        return jsonify({"message": "Unauthorized"}), 403
    
@auth_bp.route("/get_profile_by_id/<customer_id>", methods=["GET"])
@token_required
def get_profile_by_id(customer_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)

    if not customer_id:
        return jsonify({"message": "Customer ID is required."}), 400
    
    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    customers = auth.get_profile_by_id(customer_id)

    if customers:
        db.close()
        return jsonify(customers), 200
    else:
        db.close()
        return jsonify({"message": "Unauthorized"}), 403
    
@auth_bp.route("/check_role", methods=["GET"])
@token_required
def check_role():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    auth = Auth(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if auth.check_role(username):
        db.close()
        return jsonify({"message": "Access granted"}), 200
    else:
        db.close()
        return jsonify({"message": "Permission denied"}), 403