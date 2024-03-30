from flask import Blueprint, request, jsonify, session
from ..database import connector
from ..database.auth import Auth
from ..database.load_env import LoadDBEnv


manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/login', methods=['POST'])
def login():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    auth = Auth(db)
    data = request.get_json()
    manager_username = data['managerUsername']
    manager_password = data['managerPassword']

    if auth.login(manager_username, manager_password):
        session['managerUsername'] = manager_username
        db.close()
        return jsonify({'message': 'Login successful'}), 200
    else:
        db.close()
        return jsonify({'message': 'Invalid credentials'}), 401


@manager_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('managerUsername', None)
    return jsonify({'message': 'Logout successful'}), 200
    