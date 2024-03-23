from flask import Blueprint, request, jsonify, session
from ..database import connector
from ..models.auth import Auth 


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    db = connector.DBConnector()
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
    db = connector.DBConnector()
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
    db = connector.DBConnector()
    auth = Auth(db)
    data = request.get_json()
    email = data['email']

    if auth.forgot_password(email):
        db.close()
        return jsonify({'message': 'OTP sent successfully'}), 200
    else:
        db.close()
        return jsonify({'message': 'Failed to send OTP'}), 500

@auth_bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    db = connector.DBConnector()
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