from flask import Blueprint, request, jsonify, session
from main import authen as auth

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if auth.login(username, password):
        session['username'] = username
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logout successful'}), 200


@auth_bp.route('/signup', methods=['POST'])
def sign_up():
    data = request.get_json()
    username = data['username']
    password = data['password']
    full_name = data['full_name']
    email = data['email']

    if auth.sign_up(username, password, full_name, email):
        session['username'] = username
        return jsonify({'message': 'Sign-up successful'}), 201
    else:
        return jsonify({'message': 'Sign-up failed'}), 400


@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data['email']

    if auth.forgot_password(email):
        return jsonify({'message': 'OTP sent successfully'}), 200
    else:
        return jsonify({'message': 'Failed to send OTP'}), 500
