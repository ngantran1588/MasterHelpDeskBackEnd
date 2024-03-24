from flask import Blueprint, request, jsonify, session
from ..database import connector
from ..models.auth import Auth 
from ..database.load_env import LoadDBEnv


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    username = data['username']
    password = data['password']

    if auth.login(username, password):
        session['username'] = username
        db.close()
        return jsonify({'message': 'Login successful'}), 200
    else:
        db.close()
        return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/signup', methods=['POST'])
def sign_up():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    username = data['username']
    password = data['password']
    full_name = data['full_name']
    email = data['email']

    if auth.sign_up(username, password, full_name, email):
        session['username'] = username
        db.close()
        return jsonify({'message': 'Sign-up successful'}), 201
    else:
        db.close()
        return jsonify({'message': 'Sign-up failed'}), 400


@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    email = data['email']

    if auth.send_otp(email):
        db.close()
        return jsonify({'message': 'OTP sent successfully'}), 200
    else:
        db.close()
        return jsonify({'message': 'Failed to send OTP'}), 500

@auth_bp.route('/resend_otp', methods=['POST'])
def resend_otp():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    email = data['email']

    auth.delete_used_otp(email)

    if auth.send_otp(email):
        db.close()
        return jsonify({'message': 'OTP sent successfully'}), 200
    else:
        db.close()
        return jsonify({'message': 'Failed to send OTP'}), 500
    

@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    email = data["email"]
    otp = data["otp"]

    if auth.verify_otp(email, otp):
        auth.delete_used_otp(email, otp)
        db.close()
        return jsonify({'message': 'OTP verified successfully'}), 200
    else:
        auth.delete_expired_otp()
        db.close()
        return jsonify({'message': 'OTP verification failed'}), 500
    
@auth_bp.route('/change_password', methods=['POST'])
def change_password():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    username = data["username"]
    old_password = data["old_password"]
    new_password = data["new_password"]
    
    message, status = auth.change_password(username, new_password, old_password)

    if status:
        db.close()
        return jsonify({'message': message}), 200
    else:
        db.close()
        return jsonify({'message': message}), 500