from flask import Blueprint, request, jsonify
from ..database import connector
from ..database.server import Server 
from ..database.load_env import LoadDBEnv
from ..database.auth import Auth
from ..decorators import token_required
from ..server_management.server_manager import *

server_bp = Blueprint("server", __name__)


@server_bp.route("/add", methods=["POST"])
@token_required
def add_server():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)
    auth = Auth(db)
    data = request.get_json()

    server_name = data.get("server_name")
    hostname = data.get("hostname")
    organization_id = data.get("organization_id")
    username = data.get("username")
    password = data.get("password")
    rsa_key = data.get("rsa_key")
    port = data.get("port")

    username_authen = request.jwt_payload.get("username")
    if username_authen == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if auth.check_role(username_authen) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if server_manager.check_server_name_exist(server_name, organization_id):
        db.close()
        return jsonify({"message": "Organization name exists"}), 500
    
    if server_manager.check_server_slot(organization_id):
        db.close()
        return jsonify({"message": "Failed to add server slot"}), 500

    if not all([server_name, hostname, organization_id, username, password, rsa_key]):
        return jsonify({"message": "Missing required fields"}), 400

    # server_connect = ServerManager(password)

    success = server_manager.add_server(username_authen, server_name, hostname, organization_id, username, password, rsa_key, port)
    
    db.close()
    if success:
        return jsonify({"message": "Server added successfully"}), 201
    else:
        return jsonify({"message": "Failed to add server"}), 500


@server_bp.route("/update_rsa_key/<server_id>", methods=["PUT"])
@token_required
def update_rsa_key(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    new_rsa_key = data.get("rsa_key")
    
    if not new_rsa_key:
        return jsonify({"message": "Missing new RSA key"}), 400

    success = server_manager.update_rsa_key(server_id, new_rsa_key)
    
    if success:
        return jsonify({"message": "RSA key updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update RSA key"}), 500

@server_bp.route("/update_password_key/<server_id>", methods=["PUT"])
@token_required
def update_password_key(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)

    username_authen = request.jwt_payload.get("username")
   
    if username_authen == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username_authen, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    new_password_key = data.get("password")
    
    if not new_password_key:
        return jsonify({"message": "Missing new password key"}), 400

    success = server_manager.update_password_key(server_id, new_password_key)
    
    if success:
        return jsonify({"message": "password key updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update password key"}), 500

@server_bp.route("/delete/<server_id>", methods=["DELETE"])
@token_required
def delete_server(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)
    username = request.jwt_payload.get("username")
    auth = Auth()

    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if auth.check_role(username) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = server_manager.delete_server(server_id)
    
    if success:
        return jsonify({"message": "Server deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete server"}), 500


@server_bp.route("/update_information/<server_id>", methods=["PUT"])
@token_required
def update_server_information(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)

    username_authen = request.jwt_payload.get("username")
   
    if username_authen == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if server_manager.check_user_access(username_authen, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    server_name = data.get("server_name")
    hostname = data.get("hostname")
    organization_id = data.get("organization_id")
    username = data.get("username")
    port = data.get("port")
    
    if not all([server_name, hostname, organization_id, username]):
        return jsonify({"message": "Missing required fields"}), 400

    success = server_manager.update_server_information(server_id, server_name, hostname, username, port)
    
    if success:
        return jsonify({"message": "Server information updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update server information"}), 500


@server_bp.route("/get_server_data/<server_id>", methods=["GET"])
@token_required
def get_server_data(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)
    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_data = server_manager.get_server_data(server_id)
    
    if server_data:
        return jsonify(server_data), 200
    else:
        return jsonify({"message": "Server not found"}), 404


@server_bp.route("/get_server_by_id/<server_id>", methods=["GET"])
@token_required
def get_server_by_id(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)
    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
 
    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_server_by_id(server_id)
    
    if server_info:
        return jsonify(server_info), 200
    else:
        return jsonify({"message": "Server not found"}), 404


@server_bp.route("/get_number_server/<organization_id>", methods=["GET"])
@token_required
def get_number_server(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)
    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    number_server = server_manager.get_number_server(organization_id)
    
    if number_server is not None:
        return jsonify({"number_server": number_server}), 200
    else:
        return jsonify({"message": "Failed to retrieve number of servers"}), 500


@server_bp.route("/get_server_in_organization/<organization_id>", methods=["GET"])
@token_required
def get_server_in_organization(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)
    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    servers_in_organization = server_manager.get_server_in_organization(organization_id)
    
    if servers_in_organization:
        return jsonify(servers_in_organization), 200
    else:
        return jsonify({"message": "No servers found for the organization"}), 404

@server_bp.route("/add_member", methods=["PUT"])
@token_required
def add_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server = Server(db)
    auth = Auth(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    server_id = request.json["server_id"]
    new_user = request.json["new_user"]

    if not auth.exist_username(new_user):
        db.close()
        return jsonify({"message": "Username does not exist"}), 400
    
    if server.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    success = server.add_user(server_id, new_user)

    db.close()

    if success:
        return jsonify({"message": "User added to server successfully"}), 200
    else:
        return jsonify({"message": "Error adding user to server:"}), 500

@server_bp.route("/remove_member", methods=["PUT"])
@token_required
def remove_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server = Server(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    server_id = request.json["server_id"]
    remove_username = request.json["remove_username"]

    if server.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = server.remove_user(server_id, remove_username)

    db.close()

    if success:
        return jsonify({"message": "User removed from organization successfully"}), 200
    else:
        return jsonify({"message": "Failed to remove user from organization"}), 500

@server_bp.route("/get_server_info/<server_id>", methods=["GET"])
@token_required
def get_server_info(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    server_manager = Server(db)

    username = request.jwt_payload.get("username")
   
    if username == None:
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    server.connect()

    server.upload_file_to_remote("src/scripts/get_info/get_info.sh", "/root/home")

    data_return = server.execute_script_in_remote_server("/root/home/get_info.sh")

    if data_return:
        return jsonify(data_return), 200
    return jsonify({"message": "Something is wrong"}), 500


    