from flask import Blueprint, request, jsonify, send_file, make_response
from datetime import datetime
import base64
import json
import re
import shutil
from ..database import connector
from ..database.server import Server 
from ..database.load_env import LoadDBEnv
from ..database.auth import Auth
from ..const import const
from ..decorators import token_required
from ..server_management.server_manager import *

server_bp = Blueprint("server", __name__)

# Function to secure filenames (replace with a robust sanitization function)
def secure_filename(filename):
  return filename.replace("\\", "").replace("/", "")

def parse_syslog_regex(log_message):
    # Regex pattern to capture timestamp (flexible on separators) and host
    pattern = r"(\w+\s\d+\s\d+:\d+:\d+)(\s\S+)(\s(kernel)?(systemd)?.*)"

    # Match the pattern and extract groups
    match = re.match(pattern, log_message)
    if match:
        # Extract timestamp (handle cases with or without separators)
        timestamp = match.groups(1)[0]
        host = (match.groups(1)[1]).strip()
        log = (match.groups(1)[2]).strip()
    else:
        return None, None, None

    return timestamp, host, log

def parse_ufwlog_regex(log_message):
    # Regex pattern to capture timestamp (flexible on separators) and host
    pattern = r"(\w+\s\d+\s\d+:\d+:\d+)(\s.*\s)(kernel.*)"

    # Match the pattern and extract groups
    match = re.match(pattern, log_message)
    if match:
        # Extract timestamp (handle cases with or without separators)
        timestamp = match.groups(1)[0]
        host = (match.groups(1)[1]).strip()
        log = (match.groups(1)[2]).strip()
    else:
        return None, None, None

    return timestamp, host, log

def parse_lastlog_regex(log_message):
    # Regex pattern to capture timestamp (flexible on separators) and host
    pattern = r"^(\w+)\s+((pts\/\d+\s+))((\S+)?)(\s+)((\S+\s+\S+\s+.+))$"
    pattern_1 = r"^(reboot)\s+(\S+\s+boot)\s+([^ ]+)(?:\s+|\t+)(.+)$"
    pattern_2 = r"^(wtmp)\s(begins)\s(.*)$"
    # Match the pattern and extract groups
    match = re.match(pattern, log_message)
    match_1 = re.match(pattern_1, log_message)
    match_2 = re.match(pattern_2, log_message)
    if match:        
        user = match.groups(1)[0]
        info = (match.groups(1)[1]).strip()
        from_ip = (match.groups(1)[3]).strip()
        timestamp = (match.groups(1)[7]).strip()
    elif match_1:
        user = match_1.groups(1)[0]
        info = (match_1.groups(1)[1]).strip()
        from_ip = (match_1.groups(1)[2]).strip()
        timestamp = (match_1.groups(1)[3]).strip()
    elif match_2:
        user = match_2.groups(1)[0]
        info = (match_2.groups(1)[1]).strip()
        from_ip = ""
        timestamp = (match_2.groups(1)[2]).strip()
    else:
        return None, None, None, None
    return user, info, from_ip, timestamp

@server_bp.route("/add", methods=["POST"])
@token_required
def add_server():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
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

    if not all([server_name, hostname, organization_id, username]):
        return jsonify({"message": "Missing required fields"}), 400
    
    if not password and not rsa_key:
        return jsonify({"message": "Missing password or rsa key fields"}), 400
    
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
        return jsonify({"message": "Failed to check server slot"}), 500

    server = ServerManager(hostname, username, password, rsa_key)
    
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server, server information is incorrect"}), 500
    server.disconnect()
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
    db.connect()
    server_manager = Server(db)

    if not server_id:
        return jsonify({"message": "Server ID is required."}), 400

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
    db.close()
    if success:
        return jsonify({"message": "RSA key updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update RSA key"}), 500

@server_bp.route("/update_password_key/<server_id>", methods=["PUT"])
@token_required
def update_password_key(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)

    if not server_id:
        db.close()
        return jsonify({"success": False, "message": "Server ID is required."}), 400

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
    db.close()
    if success:
        return jsonify({"message": "password key updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update password key"}), 500

@server_bp.route("/delete/<server_id>", methods=["DELETE"])
@token_required
def delete_server(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    username = request.jwt_payload.get("username")
    auth = Auth(db)
    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

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
    db.close()
    if success:
        return jsonify({"message": "Server deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete server"}), 500

@server_bp.route("/update_information/<server_id>", methods=["PUT"])
@token_required
def update_server_information(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

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
    db.close()
    if success:
        return jsonify({"message": "Server information updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update server information"}), 500

@server_bp.route("/change_status/<server_id>", methods=["PUT"])
@token_required
def change_status(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username_authen = request.jwt_payload.get("username")
   
    if username_authen == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if server_manager.check_user_access(username_authen, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    status = data["status"]
    success = server_manager.update_status(server_id, status)
    db.close()
    if success:
        return jsonify({"message": "Status updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update status"}), 500
    
@server_bp.route("/get_server_data/<server_id>", methods=["GET"])
@token_required
def get_server_data(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    username = request.jwt_payload.get("username")

    if not server_id:
        return jsonify({"message": "Server ID is required."}), 400
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_data = server_manager.get_server_data(server_id)
    db.close()
    if server_data:
        return jsonify(server_data), 200
    else:
        return jsonify({"message": "Server not found"}), 404

@server_bp.route("/get_server_by_id/<server_id>", methods=["GET"])
@token_required
def get_server_by_id(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    username = request.jwt_payload.get("username")

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
 
    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_server_by_id(server_id)
    db.close()
    if server_info:
        return jsonify(server_info), 200
    else:
        return jsonify({"message": "Server not found"}), 404

@server_bp.route("/get_number_server/<organization_id>", methods=["GET"])
@token_required
def get_number_server(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    username = request.jwt_payload.get("username")

    if not organization_id:
        db.close()
        return jsonify({"message": "Organization ID is required."}), 400
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    number_server = server_manager.get_number_server(organization_id)
    db.close()
    if number_server is not None:
        return jsonify({"number_server": number_server}), 200
    else:
        return jsonify({"message": "Failed to retrieve number of servers"}), 500

@server_bp.route("/get_server_in_organization/<organization_id>", methods=["GET"])
@token_required
def get_server_in_organization(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    username = request.jwt_payload.get("username")

    if not organization_id:
        db.close()
        return jsonify({"message": "Organization ID is required."}), 400
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    servers_in_organization = server_manager.get_server_in_organization(organization_id)
    db.close()
    if servers_in_organization:
        return jsonify(servers_in_organization), 200
    else:
        return jsonify({"message": "No servers found for the organization"}), 404

@server_bp.route("/add_member", methods=["PUT"])
@token_required
def add_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
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
    success, msg = server.add_user(server_id, new_user)

    db.close()

    if success:
        return jsonify({"message": msg}), 200
    else:
        return jsonify({"message": msg}), 500

@server_bp.route("/remove_member", methods=["PUT"])
@token_required
def remove_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
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
    
    success, msg = server.remove_user(server_id, remove_username)

    db.close()

    if success:
        return jsonify({"message": msg}), 200
    else:
        return jsonify({"message": msg}), 500

@server_bp.route("/get_server_members/<server_id>", methods=["GET"])
@token_required
def get_server_members(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server = Server(db)
    auth = Auth(db)

    username = request.jwt_payload.get("username")

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    server_members = server.get_server_members(server_id)
    
    if len(server_members) > 0 :
        list_member = auth.get_role_of_members(server_members)
        if list_member == None:
            db.close()
            return jsonify({"message": "Error in querying server member"}), 403
        db.close()
        return jsonify({"members": list_member}), 200
    db.close()
    return jsonify({"message": "Server not found or there is no member in server"}), 403

@server_bp.route("/get_remain_slot/<organization_id>", methods=["GET"])
@token_required
def get_remain_slot(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server = Server(db)
    
    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not organization_id:
        db.close()
        return jsonify({"message": "Organization ID is required."}), 400

    remain_slot = server.get_remain_slot(organization_id)
    db.close()

    if remain_slot:
        return jsonify({"slot": remain_slot}), 200
    else:
        return jsonify({"message": "Error in querying remain slot"}), 500

@server_bp.route("/get_server_info/<server_id>", methods=["GET"])
@token_required
def get_server_info(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    info_path = os.environ.get("SCRIPT_PATH_GET_INFO")
    script_directory = os.environ.get("SERVER_DIRECTORY")

    file_name = server.get_file_name(info_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(info_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        data = json.loads(data_return)

        # Add new key-value pair
        data["script_directory"] = script_directory
        data["last_seen"] = str(datetime.now())

        # Convert dictionary back to JSON string
        updated_json_str = json.dumps(data)
        return updated_json_str, 200
    return stderr, 500

@server_bp.route("/get_all_proxy/<server_id>", methods=["GET"])
@token_required
def get_all_proxy(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_PROXY):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    proxy_path = os.environ.get("SCRIPT_PATH_GET_ALL_PROXY")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(proxy_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(proxy_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        data = json.loads(data_return)
        updated_json_str = json.dumps(data)
        return updated_json_str, 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/update_proxy/<server_id>", methods=["POST"])
@token_required
def update_proxy(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not auth.check_role_access(username, const.TAB_PROXY):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

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
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
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
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, old_domain, old_port, new_domain, new_port)
    server.disconnect()
    if data_return:
        return data_return, 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/add_proxy/<server_id>", methods=["POST"])
@token_required
def add_proxy(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_PROXY):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    data = request.json

    protocol = data["protocol"]
    domain = data["domain"]
    port = data["port"]

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
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
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, domain, port)
    server.disconnect()
    if data_return:
        return data_return, 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/delete_proxy/<server_id>", methods=["DELETE"])
@token_required
def delete_proxy(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_PROXY):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    data = request.json

    protocol = data["protocol"]
    detail = data["detail"]
    input_data = str(detail).split("//")
    input_data = input_data[1].split(":")
    domain = input_data[0]
    port = input_data[1]

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
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
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, domain, port)
    server.disconnect()
    if data_return:
        return data_return, 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/lib_status/<server_id>", methods=["GET"])
@token_required
def lib_status(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not auth.check_role_access(username, const.TAB_LIB):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500
    
    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"]) 

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500

    action_path = os.environ.get("SCRIPT_PATH_LIB_INSTALL")

    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(action_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(action_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()

    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        data_list = []
        for line in data_return.splitlines():
            data_dict = json.loads(line)  # Assuming each line is a JSON string
            data_list.append(data_dict)
        return data_list, 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/install_lib/<server_id>", methods=["POST"])
@token_required
def install_lib(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 

    if not auth.check_role_access(username, const.TAB_LIB):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    data = request.get_json()

    library = data["library"]

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"]) 

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
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
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        data_return = data_return.split("\n")
        return jsonify({"lines": data_return})
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/uninstall_lib/<server_id>", methods=["POST"])
@token_required
def uninstall_lib(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_LIB):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    data = request.json

    library = data["library"]
    
    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
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
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        data_return = data_return.split("\n")
        return jsonify({"lines": data_return})
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/firewall_action/<server_id>", methods=["POST"])
@token_required
def firewall_action(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_FIREWALL):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    data = request.json

    action = data["action"]
    port = data.get("port")
    ip = data.get("ip")

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    arg = None
    if action == "allow_ip":
        action_path = os.environ.get("SCRIPT_PATH_ALLOW_IP")
        if not ip or ip == "":
            db.close()
            return jsonify({"message":"IP required"}), 500
        arg = ip
    elif action == "allow_port":
        action_path = os.environ.get("SCRIPT_PATH_ALLOW_PORT")
        if not port or port == "":
            db.close()
            return jsonify({"message":"Port required"}), 500
        arg = port
    elif action == "deny_ip":
        action_path = os.environ.get("SCRIPT_PATH_DENY_IP")
        if not ip or ip == "":
            db.close()
            return jsonify({"message":"IP required"}), 500
        arg = ip
    elif action == "deny_port":
        action_path = os.environ.get("SCRIPT_PATH_DENY_PORT")
        if not port or port == "":
            db.close()
            return jsonify({"message":"Port required"}), 500
        arg = port
    elif action == "enable_firewall":
        action_path = os.environ.get("SCRIPT_PATH_ENABLE_FIREWALL")
    elif action == "disable_firewall":
        action_path = os.environ.get("SCRIPT_PATH_DISABLE_FIREWALL")
    elif action == "reset_firewall":
        action_path = os.environ.get("SCRIPT_PATH_RESET_FIREWALL")
    elif action == "allow_ssh":
        action_path = os.environ.get("SCRIPT_PATH_ALLOW_SSH")
    elif action == "deny_ssh":
        action_path = os.environ.get("SCRIPT_PATH_DENY_SSH")
    elif action == "allow_telnet":
        action_path = os.environ.get("SCRIPT_PATH_ALLOW_TELNET")
    elif action == "deny_telnet":
        action_path = os.environ.get("SCRIPT_PATH_DENY_TELNET")
    
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(action_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(action_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, arg)
    server.disconnect()
    if data_return:
        data_return = data_return.split("\n")
        return jsonify({"lines": data_return})
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/firewall_rules/<server_id>", methods=["POST"])
@token_required
def firewall_rules(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_FIREWALL):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    action_path = os.environ.get("SCRIPT_PATH_SHOW_STATUS")

    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(action_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(action_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        # Parse the output
        lines = data_return.split("\n")
        rules = []
        
        for line in lines:
            if not line.startswith("--"):
                line = re.sub(r"(?<!\w)\s+(?!\w)", ",", line)
                columns = line.split(",")
                if len(columns) >= 3:
                    if columns[0].replace(" ", "") == "To":
                        continue
                    to = columns[0]
                    action = columns[1]
                    frm = " ".join(columns[2:])
                    rules.append({"to": to, "action": action, "from": frm})

        return json.dumps(rules, indent=4), 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/docker_build/<server_id>", methods=["POST"])
@token_required
def docker_build(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DOCKER):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    data = request.json

    dockerfile = data.get("dockerfile")
    image_tag = data.get("image_tag")

    if not dockerfile or not image_tag:
        db.close()
        return jsonify({"message":"No data for docker build"}), 500
    
    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    docker_path = os.environ.get("SCRIPT_PATH_DOCKER_CONTROL")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(docker_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(dockerfile):
        db.close()
        return jsonify({"message": "Please upload folder to server"}), 500
    
    dockerfile_path = f"{dockerfile}/Dockerfile"
    if not server.check_script_exists_on_remote(dockerfile_path):
        db.close()
        return jsonify({"message": "Please upload Dockerfile to server"}), 500
    
    if not server.check_script_exists_on_remote(file_in_server):
        db.close()
        server.upload_file_to_remote(docker_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, "build", dockerfile, image_tag)
    server.disconnect()
    if data_return:
        data_return = data_return.split("\n")
        return jsonify({"lines": data_return})
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/docker_containers/<server_id>", methods=["POST"])
@token_required
def docker_containers(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DOCKER):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    data = request.json

    container = data.get("container")
    action = data.get("action")

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    if not container or not action:
        return jsonify({"message":"No data for container"}), 500

    docker_path = os.environ.get("SCRIPT_PATH_DOCKER_CONTROL")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(docker_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(docker_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, action, container)
    server.disconnect()
    if data_return:
        data_return = data_return.split("\n")
        return jsonify({"lines": data_return})
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/docker_create_containers/<server_id>", methods=["POST"])
@token_required
def docker_create_containers(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DOCKER):
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    data = request.json

    image = data.get("image")
    container_name = data.get("container_name")

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    if not image or not container_name:
        db.close()
        return jsonify({"message":"No data for container"}), 500

    docker_path = os.environ.get("SCRIPT_PATH_DOCKER_CONTROL")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(docker_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(docker_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, "create", image, container_name)
    server.disconnect()
    if data_return:
        data_return = data_return.split("\n")
        return jsonify({"lines": data_return})
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/docker_compose/<server_id>", methods=["POST"])
@token_required
def docker_compose(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if server_manager.check_user_access(username, server_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DOCKER):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    data = request.json

    compose_yaml = data.get("compose_yaml")
    action = data.get("action")

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    # Connect to the server
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    if not compose_yaml:
        db.close()
        return jsonify({"message":"No data for docker compose"}), 500

    docker_path = os.environ.get("SCRIPT_PATH_DOCKER_CONTROL")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(docker_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(docker_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, action, compose_yaml)
    server.disconnect()
    if data_return:
        data_return = data_return.split("\n")
        return jsonify({"lines": data_return})
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/docker_list_images/<server_id>", methods=["GET"])
@token_required
def docker_list_images(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DOCKER):
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])
    
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    docker_path = os.environ.get("SCRIPT_PATH_DOCKER_CONTROL")
    script_directory = os.environ.get("SERVER_DIRECTORY")

    file_name = server.get_file_name(docker_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(docker_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, "list-images")
    server.disconnect()
    if data_return:
        # Parse the output
        lines = data_return.split("\n")
        images = []
        for line in lines:
            line = re.sub(r"(?<!\w)\s+(?!\w)", ",", line)
            columns = line.split(",")
            if len(columns) >= 5 and columns[0].replace(" ", "") != "REPOSITORY":
                image = {
                    "repository": columns[0].replace(" ", ""),
                    "tag": columns[1].replace(" ", ""),
                    "image_id": columns[2].replace(" ", ""),
                    "size": columns[4].replace(" ", ""),
                    "created": columns[3]
                }
                
                images.append(image)
        return json.dumps(images, indent=4), 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/docker_list_containers/<server_id>", methods=["GET"])
@token_required
def docker_list_containers(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DOCKER):
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    server_info = server_manager.get_info_to_connect(server_id)
  
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    docker_path = os.environ.get("SCRIPT_PATH_DOCKER_CONTROL")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(docker_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(docker_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, "list-containers")
    server.disconnect()
    if data_return:
        # Parse the output
        lines = data_return.split("\n")
        rules = []
      
        for line in lines:
            line = re.sub(r"(?<!\w)\s+(?!\w)", ",", line)
            columns = line.split(",")
            if columns[0].replace(" ", "") == "CONTAINERID" or len(columns) <= 1:
                continue
            container_id = columns[0].replace(" ", "")
            image = columns[1]
            command = columns[2]
            created = columns[3]
            status = columns[4]
            if len(columns)>= 7:
                ports = columns[5]
                names = columns[6]
            else:
                ports = None
                names = columns[5]
            rules.append({"container_id": container_id, "image": image, "command": command, "created": created, "status": status, "ports": ports, "names": names})
        return json.dumps(rules, indent=4), 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/execute_code/<server_id>", methods=["POST"])
@token_required
def execute_code(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not auth.check_role_access(username, const.TAB_EXECUTION):
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    data = request.get_json()

    execute_file = data.get("execute_file")

    if not execute_file:
        db.close()
        return jsonify({"message":"Execute file is required"}), 500
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500

    if not server.check_script_exists_on_remote(execute_file):
        db.close()
        return jsonify({"message": "File does not exist on server"}), 500

    execute_code_path = os.environ.get("SCRIPT_PATH_EXECUTE_CODE")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(execute_code_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(execute_code_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    server.grant_permission(execute_file, 700)
    data_return, stderr = server.execute_script_in_remote_server(file_in_server, execute_file)
    server.disconnect()
    if data_return:
        # Parse the output
        lines = data_return.split("\n")
        lines.remove("")
    else:
        lines = None
    if not stderr and not data_return:
        return jsonify({"message":"Can not execute code on server"}), 500
    if stderr:
        error_messages = stderr.split("\n")
    return jsonify({"lines": lines, "stderr": error_messages}), 200

@server_bp.route("/report_log_syslog/<server_id>", methods=["POST"])
@token_required
def report_log_syslog(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_LOG):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])
    
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    execute_code_path = os.environ.get("SCRIPT_PATH_LOG_SYSLOG")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(execute_code_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(execute_code_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        # Parse the output
        lines = data_return.split("\n")
        lines.remove("")
        parsed_log = []
        for line in lines:
            timestamp, host, log = parse_syslog_regex(line)
            if timestamp == None or host == None or log == None:
                return jsonify({"message": "Error in parsing log"}), 500
            
            parsed_log.append({"timestamp": timestamp, "host": host, "log": log})
        return jsonify({"parsed_log": parsed_log}), 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/report_raw_syslog/<server_id>", methods=["GET"])
@token_required
def report_raw_syslog(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_LOG):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    execute_code_path = os.environ.get("SCRIPT_PATH_LOG_SYSLOG")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(execute_code_path)
    file_in_server = f"{script_directory}/{file_name}"
   
    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(execute_code_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        local_file_path = os.environ.get("TMP_FOLDER")
        local_file_path = os.path.join(local_file_path, server_id)

        try:
            os.makedirs(local_file_path)
        except OSError as e:
            if "file already exists" in str(e):  # Check for file/folder existence in error message
                print(f"Folder '{local_file_path}' already exists.")
            else:
                print(f"Error creating folder: {e}")
        
        filename = os.environ.get("LOG_SYSLOG")
        local_file_path = os.path.join(local_file_path, filename)

        with open(local_file_path, 'w') as f:  # Open the file in write mode ('w')
            if isinstance(data_return, str):  # Check if data is a single string
                f.write(data_return)
            else:  # Assume data is a list of strings
                f.writelines(data_return)  # Write each line in the list

        response = make_response(send_file(local_file_path, mimetype="application/octet-stream", as_attachment=True, download_name=filename))    
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        
        return response, 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return stderr, 500

@server_bp.route("/report_log_last/<server_id>", methods=["POST"])
@token_required
def report_log_last(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_LOG):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 

    execute_code_path = os.environ.get("SCRIPT_PATH_LOG_LAST")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(execute_code_path)
    file_in_server = f"{script_directory}/{file_name}"

    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(execute_code_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        # Parse the output
        lines = data_return.split("\n")
        lines.remove("")
        parsed_log = []
        for line in lines:
            if line == "":
                continue
            user, info, from_ip, timestamp = parse_lastlog_regex(line)
            if user == None or info == None or from_ip == None or timestamp == None:
                return jsonify({"message": "Error in parsing log"}), 500
            
            parsed_log.append({"user": user, "info": info, "from_ip": from_ip, "timestamp": timestamp})
        return jsonify({"parsed_log": parsed_log}), 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/report_raw_log_last/<server_id>", methods=["GET"])
@token_required
def report_raw_log_last(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_LOG):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    execute_code_path = os.environ.get("SCRIPT_PATH_LOG_LAST")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(execute_code_path)
    file_in_server = f"{script_directory}/{file_name}"
   
    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(execute_code_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        local_file_path = os.environ.get("TMP_FOLDER")
        local_file_path = os.path.join(local_file_path, server_id)

        try:
            os.makedirs(local_file_path)
        except OSError as e:
            if "file already exists" in str(e):  # Check for file/folder existence in error message
                print(f"Folder '{local_file_path}' already exists.")
            else:
                print(f"Error creating folder: {e}")
        
        filename = os.environ.get("LOG_LASTLOG")
        local_file_path = os.path.join(local_file_path, filename)

        with open(local_file_path, 'w') as f:  # Open the file in write mode ('w')
            if isinstance(data_return, str):  # Check if data is a single string
                f.write(data_return)
            else:  # Assume data is a list of strings
                f.writelines(data_return)  # Write each line in the list

        response = make_response(send_file(local_file_path, mimetype="application/octet-stream", as_attachment=True, download_name=filename))    
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        
        return response, 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/report_log_ufw/<server_id>", methods=["POST"])
@token_required
def report_log_ufw(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_LOG):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    execute_code_path = os.environ.get("SCRIPT_PATH_LOG_UFW")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(execute_code_path)
    file_in_server = f"{script_directory}/{file_name}"
   
    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(execute_code_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        # Parse the output
        lines = data_return.split("\n")
        lines.remove("")
        parsed_log = []
        for line in lines:
            timestamp, host, log = parse_ufwlog_regex(line)
            if timestamp == None or host == None or log == None:
                return jsonify({"message": "Error in parsing log"}), 500
            
            parsed_log.append({"timestamp": timestamp, "host": host, "log": log})
        return jsonify({"parsed_log": parsed_log}), 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/report_raw_log_ufw/<server_id>", methods=["GET"])
@token_required
def report_raw_log_ufw(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_LOG):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])

    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500
    
    execute_code_path = os.environ.get("SCRIPT_PATH_LOG_UFW")
    script_directory = os.environ.get("SERVER_DIRECTORY")
    
    file_name = server.get_file_name(execute_code_path)
    file_in_server = f"{script_directory}/{file_name}"
   
    if not server.check_script_exists_on_remote(file_in_server):
        server.upload_file_to_remote(execute_code_path, script_directory)
        server.grant_permission(file_in_server, 700)
    db.close()
    data_return, stderr = server.execute_script_in_remote_server(file_in_server)
    server.disconnect()
    if data_return:
        local_file_path = os.environ.get("TMP_FOLDER")
        local_file_path = os.path.join(local_file_path, server_id)

        try:
            os.makedirs(local_file_path)
        except OSError as e:
            if "file already exists" in str(e):  # Check for file/folder existence in error message
                print(f"Folder '{local_file_path}' already exists.")
            else:
                print(f"Error creating folder: {e}")
        
        filename = os.environ.get("LOG_UFWLOG")
        local_file_path = os.path.join(local_file_path, filename)

        with open(local_file_path, 'w') as f:  # Open the file in write mode ('w')
            if isinstance(data_return, str):  # Check if data is a single string
                f.write(data_return)
            else:  # Assume data is a list of strings
                f.writelines(data_return)  # Write each line in the list

        response = make_response(send_file(local_file_path, mimetype="application/octet-stream", as_attachment=True, download_name=filename))    
        response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        
        return response, 200
    if stderr:
        error_messages = stderr.split("\n")
        return jsonify({"stderr": error_messages}), 500
    return jsonify({"message": "Something is wrong"}), 404

@server_bp.route("/upload_file/<server_id>", methods=["POST"])
@token_required
def upload_file(server_id):
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400
    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"message": "No selected file"}), 400
    if not uploaded_file:
        return jsonify({"message": "File upload failed"}), 400
    dir = request.form.get("dir", None)
    if dir == None:
        dir = os.environ.get("DEFAULT_FOLDER")
    if dir == "undefined":
        return jsonify({"message": "File path is required"}), 400
    filename = uploaded_file.filename

    if dir[-1] != "/":
        dir = dir + "/"
        
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)
    upload_folder_tmp = os.environ.get("TMP_FOLDER")
    upload_folder_tmp = os.path.join(upload_folder_tmp, server_id)
    
    try:
        os.makedirs(upload_folder_tmp)
    except OSError as e:
        if "file already exists" in str(e):  # Check for file/folder existence in error message
            print(f"Folder '{upload_folder_tmp}' already exists.")
        else:
            print(f"Error creating folder: {e}")

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DATA):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500
    
    filename = secure_filename(filename)
    local_filepath = os.path.join(upload_folder_tmp, filename)
    uploaded_file.save(local_filepath)

    remote_filepath = os.path.join(dir, filename)
   
    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500

    if server.check_script_exists_on_remote(remote_filepath):
        return jsonify({"message":"File exists on server"}), 500
    db.close()
    server.upload_file_to_remote(local_filepath, dir)
    server.disconnect()
    try:
        os.remove(local_filepath)
        print(f"Local file deleted: {local_filepath}")
        return jsonify({"message": "Upload file success"}), 200
    except OSError as e:
        print(f"Error deleting local file: {e}")
        return jsonify({"message": "Upload file failed"}), 500

@server_bp.route("/upload_folder/<server_id>", methods=["POST"])
@token_required
def upload_folder(server_id):
    if "zip_file" not in request.files:
        return jsonify({"message": "No file part"}), 400
    uploaded_file = request.files["zip_file"]
    if uploaded_file.filename == "":
        return jsonify({"message": "No selected file"}), 400
    if not uploaded_file:
        return jsonify({"message": "File upload failed"}), 400
    dir = request.form.get("dir", None)
    if dir == None:
        dir = os.environ.get("DEFAULT_FOLDER")
    if dir == "undefined":
        return jsonify({"message": "File path is required"}), 400
    if dir[-1] != "/":
        dir = dir + "/"
    filename = uploaded_file.filename

    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)
    upload_folder_tmp = os.environ.get("TMP_FOLDER")
    upload_folder_tmp = os.path.join(upload_folder_tmp, server_id)
    
    try:
        os.makedirs(upload_folder_tmp)
    except OSError as e:
        if "file already exists" in str(e):  # Check for file/folder existence in error message
            print(f"Folder '{upload_folder_tmp}' already exists.")
        else:
            print(f"Error creating folder: {e}")

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DATA):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500
    
    filename = secure_filename(filename)
    local_filepath = os.path.join(upload_folder_tmp, filename)
    uploaded_file.save(local_filepath)
    db.close()
   
    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500

    extracted_folder = os.path.splitext(filename)[0]
    remote_filepath = os.path.join(dir, extracted_folder)

    if server.check_script_exists_on_remote(remote_filepath):
        return jsonify({"message":"Folder exists on server"}), 500
    
    with zipfile.ZipFile(local_filepath, "r") as zip_ref:
        extract_path = os.path.join(os.path.dirname(local_filepath), extracted_folder)
        os.makedirs(extract_path, exist_ok=True)
        zip_ref.extractall(extract_path)

    server.upload_folder(extract_path, dir)
    server.disconnect()
    try:
        os.remove(local_filepath)
        print(f"Local file deleted: {local_filepath}")
        shutil.rmtree(extract_path)
        print(f"Local folder deleted: {extract_path}")
        return jsonify({"message": "Upload file success"}), 200
    except OSError as e:
        print(f"Error deleting local file: {e}")
        return jsonify({"message": "Upload file failed"}), 500
    
@server_bp.route("/download_file/<server_id>", methods=["GET"])
@token_required
def download_file(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DATA):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500
    db.close()

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500

    file_path_encoded = request.args.get("file")
    file_path = base64.b64decode(file_path_encoded).decode('utf-8')
    if file_path == None:
        db.close()
        return jsonify({"messsage": "File path is required"}), 500
    file_path = str(file_path)
   
    if not server.check_script_exists_on_remote(file_path) :
        db.close()
        return jsonify({"messsage": "File path does not exist"}), 500
    
    local_file_path = os.environ.get("TMP_FOLDER")
    local_file_path = os.path.join(local_file_path, server_id)

    try:
        os.makedirs(local_file_path)
    except OSError as e:
        if "file already exists" in str(e):  # Check for file/folder existence in error message
            print(f"Folder '{local_file_path}' already exists.")
        else:
            print(f"Error creating folder: {e}")
   
    server.download_file_from_remote(file_path, local_file_path)
    filename = os.path.basename(file_path)
    local_file_path = os.path.join(local_file_path, filename)

    server.disconnect()
    
    response = make_response(send_file(local_file_path, mimetype="application/octet-stream", as_attachment=True, download_name=filename))    
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    
    return response, 200

@server_bp.route("/download_folder/<server_id>", methods=["GET"])
@token_required
def download_folder(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if not auth.check_role_access(username, const.TAB_DATA):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500
    db.close()

    server = ServerManager(server_info["hostname"], server_info["username"], server_info["password"], server_info["rsa_key"])
    result = server.connect()
    if not result:
        db.close()
        return jsonify({"message": "Can not connect server"}), 500

    folder_path_encoded = request.args.get("folder")
    folder_path = base64.b64decode(folder_path_encoded).decode('utf-8')
    if folder_path == None:
        db.close()
        return jsonify({"messsage": "Folder path is required"}), 500
    folder_path = str(folder_path)
   
    if not server.check_script_exists_on_remote(folder_path) :
        db.close()
        return jsonify({"messsage": "Folder path does not exist"}), 500
    
    local_folder_path = os.environ.get("TMP_FOLDER")
    local_folder_path = os.path.join(local_folder_path, server_id)

    try:
        os.makedirs(local_folder_path)
    except OSError as e:
        if "file already exists" in str(e):  # Check for file/folder existence in error message
            print(f"Folder '{local_folder_path}' already exists.")
        else:
            print(f"Error creating folder: {e}")
   
    server.download_folder(folder_path, local_folder_path)
    filename = os.path.basename(folder_path)
    filename_zip = f"{filename}.zip"
    local_folder_path = os.path.join(local_folder_path, filename_zip)

    server.disconnect()
    
    response = make_response(send_file(local_folder_path, mimetype="application/zip", as_attachment=True, download_name=filename_zip))    
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    
    return response, 200

@server_bp.route("/confirm_download/<server_id>", methods=["POST"])
@token_required
def confirm_download(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    server_info = server_manager.get_info_to_connect(server_id)
    if server_info == None:
        db.close()
        return jsonify({"message":"No data for server"}), 500
    db.close()

    data = request.get_json()
    filename = data.get("filename", None)
    if filename == None:
        return jsonify({"message": "File name is required."}), 400
    
    local_file_path = os.environ.get("TMP_FOLDER")
    local_file_path = os.path.join(local_file_path, server_id, filename)

    try:
        os.remove(local_file_path)
        print(f"Local file deleted: {local_file_path}")
        return jsonify({"message": "Upload file success"}), 200
    except OSError as e:
        print(f"Error deleting local file: {e}")
        return jsonify({"message": "Upload file failed"}), 500

@server_bp.route("/check_role_access/<server_id>", methods=["GET"])
@token_required
def check_role_access(server_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    server_manager = Server(db)
    auth = Auth(db)

    if not server_id:
        db.close()
        return jsonify({"message": "Server ID is required."}), 400

    username = request.jwt_payload.get("username")
    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if not server_manager.check_user_access(username, server_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()

    tab = data["tab"]

    if not auth.check_role_access(username, tab):
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    return jsonify({"message": "Access allowed"}), 200