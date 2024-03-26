from flask import Blueprint, request, jsonify, session
from ..database import connector
from ..models.auth import Auth 
from ..database.load_env import LoadDBEnv


auth_bp = Blueprint('organization', __name__)

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