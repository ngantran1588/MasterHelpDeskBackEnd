from flask import Blueprint, request, jsonify
from datetime import datetime
import json
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
        return jsonify({"message": "Server name exists"}), 500
    
    if server_manager.check_server_slot(organization_id):
        db.close()
        return jsonify({"message": "Failed to add server slot"}), 500

    if not all([server_name, hostname, organization_id, username]):
        return jsonify({"message": "Missing required fields"}), 400

    if not password and not rsa_key:
        return jsonify({"message": "Missing password or rsa key fields"}), 400
    
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
    auth = Auth(db)

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
    if server_info == None:
        return jsonify({"message":"No data for server"}, 500)

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    server.connect()
    
    info_path = os.environ.get("SCRIPT_PATH_GET_INFO")
    script_directory = os.environ.get("SERVER_DIRECTORY")

    file_name = server.get_file_name(info_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(info_path, script_directory)
        server.grant_permission(file_in_server, 700)

    data_return = server.execute_script_in_remote_server(file_in_server)
    
    if data_return:
        data = json.loads(data_return)

        # Add new key-value pair
        data["script_directory"] = script_directory
        data["last_seen"] = str(datetime.now())

        # Convert dictionary back to JSON string
        updated_json_str = json.dumps(data)
        return updated_json_str, 200
    return jsonify({"message": "Something is wrong"}), 500


@server_bp.route("/get_all_proxy/<server_id>", methods=["GET"])
@token_required
def get_all_proxy(server_id):
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
    if server_info == None:
        return jsonify({"message":"No data for server"}, 500)

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    server.connect()
    
    proxy_path = os.environ.get("SCRIPT_PATH_GET_ALL_PROXY")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(proxy_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(proxy_path, script_directory)
        server.grant_permission(file_in_server, 700)

    data_return = server.execute_script_in_remote_server(file_in_server)
    
    if data_return:
        data = json.loads(data_return)
        updated_json_str = json.dumps(data)
        return updated_json_str, 200
    return jsonify({"message": "Something is wrong"}), 500

@server_bp.route("/update_proxy/<server_id>", methods=["POST"])
@token_required
def update_proxy(server_id):
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
    if server_info == None:
        return jsonify({"message":"No data for server"}, 500)

    data = request.json

    protocol = data["protocol"]
    detail = data["detail"]
    input_data = str(detail).split("//")
    input_data = input_data[1].split(":")
    old_domain = input_data[0]
    old_port = input_data[1]
    new_domain = data["new_domain"]
    new_port = data["new_port"]

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    server.connect()
    
    if protocol == "ftp_proxy":
        proxy_path = os.environ.get("SCRIPT_PATH_UPDATE_FTP_PROXY")
    elif protocol == "http_proxy":
        proxy_path = os.environ.get("SCRIPT_PATH_UPDATE_HTTP_PROXY")
    elif protocol == "https_proxy":
        proxy_path = os.environ.get("SCRIPT_PATH_UPDATE_HTTPS_PROXY")

    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(proxy_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(proxy_path, script_directory)
        server.grant_permission(file_in_server, 700)

    data_return = server.execute_script_in_remote_server(file_in_server, old_domain, old_port, new_domain, new_port)
    
    if data_return:
        return data_return, 200
    return jsonify({"message": "Something is wrong"}), 500

@server_bp.route("/add_proxy/<server_id>", methods=["POST"])
@token_required
def add_proxy(server_id):
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
    if server_info == None:
        return jsonify({"message":"No data for server"}, 500)

    data = request.json

    protocol = data["protocol"]
    detail = data["detail"]
    input_data = str(detail).split("//")
    input_data = input_data[1].split(":")
    domain = input_data[0]
    port = input_data[1]

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    server.connect()
    
    if protocol == "ftp_proxy":
        proxy_path = os.environ.get("SCRIPT_PATH_FTP_PROXY")
    elif protocol == "http_proxy":
        proxy_path = os.environ.get("SCRIPT_PATH_HTTP_PROXY")
    elif protocol == "https_proxy":
        proxy_path = os.environ.get("SCRIPT_PATH_HTTPS_PROXY")

    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(proxy_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(proxy_path, script_directory)
        server.grant_permission(file_in_server, 700)

    data_return = server.execute_script_in_remote_server(file_in_server, domain, port)
    
    if data_return:
        return data_return, 200
    return jsonify({"message": "Something is wrong"}), 500

@server_bp.route("/delete_proxy/<server_id>", methods=["DELETE"])
@token_required
def delete_proxy(server_id):
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
    if server_info == None:
        return jsonify({"message":"No data for server"}, 500)

    data = request.json

    protocol = data["protocol"]
    detail = data["detail"]
    input_data = str(detail).split("//")
    input_data = input_data[1].split(":")
    domain = input_data[0]
    port = input_data[1]

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    server.connect()
    
    if protocol == "ftp_proxy":
        proxy_path = os.environ.get("SCRIPT_PATH_DELETE_FTP_PROXY")
    elif protocol == "http_proxy":
        proxy_path = os.environ.get("SCRIPT_PATH_DELETE_HTTP_PROXY")
    elif protocol == "https_proxy":
        proxy_path = os.environ.get("SCRIPT_PATH_DELETE_HTTPS_PROXY")

    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(proxy_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(proxy_path, script_directory)
        server.grant_permission(file_in_server, 700)

    data_return = server.execute_script_in_remote_server(file_in_server, domain, port)
    
    if data_return:
        return data_return, 200
    return jsonify({"message": "Something is wrong"}), 500

@server_bp.route("/install_lib/<server_id>", methods=["POST"])
@token_required
def install_lib(server_id):
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
    if server_info == None:
        return jsonify({"message":"No data for server"}, 500)

    data = request.json

    library = data["library"]

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    server.connect()
    
    if library == "docker":
        library_path = os.environ.get("SCRIPT_PATH_LIB_INSTALL_DOCKER")
    elif library == "mongodb":
        library_path = os.environ.get("SCRIPT_PATH_LIB_INSTALL_MONGODB")
    elif library == "nginx":
        library_path = os.environ.get("SCRIPT_PATH_LIB_INSTALL_NGINX")
    elif library == "pip":
        library_path = os.environ.get("SCRIPT_PATH_LIB_INSTALL_PIP")
    elif library == "postgre":
        library_path = os.environ.get("SCRIPT_PATH_LIB_INSTALL_POSTGRE") 
    elif library == "python":
        library_path = os.environ.get("SCRIPT_PATH_LIB_INSTALL_PYTHON")

    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(library_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(library_path, script_directory)
        server.grant_permission(file_in_server, 700)

    data_return = server.execute_script_in_remote_server(file_in_server)
    
    if data_return:
        return data_return, 200
    return jsonify({"message": "Something is wrong"}), 500

@server_bp.route("/uninstall_lib/<server_id>", methods=["POST"])
@token_required
def uninstall_lib(server_id):
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
    if server_info == None:
        return jsonify({"message":"No data for server"}, 500)

    data = request.json

    library = data["library"]

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    server.connect()
    
    if library == "docker":
        library_path = os.environ.get("SCRIPT_PATH_LIB_UNINSTALL_DOCKER")
    elif library == "mongodb":
        library_path = os.environ.get("SCRIPT_PATH_LIB_UNINSTALL_MONGODB")
    elif library == "nginx":
        library_path = os.environ.get("SCRIPT_PATH_LIB_UNINSTALL_NGINX")
    elif library == "pip":
        library_path = os.environ.get("SCRIPT_PATH_LIB_UNINSTALL_PIP")
    elif library == "postgre":
        library_path = os.environ.get("SCRIPT_PATH_LIB_UNINSTALL_POSTGRE")
    elif library == "python":
        library_path = os.environ.get("SCRIPT_PATH_LIB_UNINSTALL_PYTHON")


    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(library_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(library_path, script_directory)
        server.grant_permission(file_in_server, 700)

    data_return = server.execute_script_in_remote_server(file_in_server)
    
    if data_return:
        return data_return, 200
    return jsonify({"message": "Something is wrong"}), 500