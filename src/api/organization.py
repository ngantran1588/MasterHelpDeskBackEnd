from flask import Blueprint, request, jsonify, session, current_app
from ..database import connector
from ..database.organization import Organization 
from ..database.load_env import LoadDBEnv
from ..database.auth import Auth
from flask_jwt_extended import jwt_required, get_jwt_identity

organization_bp = Blueprint("organization", __name__)

@organization_bp.route("/add", methods=["POST"])
@jwt_required()
def add_organization():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)
    auth = Auth(db)

    jwt = current_app.config["jwt"]

    username = get_jwt_identity()
    
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    name = data["name"]
    contact_phone = data["contact_phone"]
    contact_email = data["contact_email"]
    description = data["description"]
    username = session["username"]
    org_member = data["org_member"]

    if org.check_organization_slot(username) == False:
        db.close()
        return jsonify({"message": "Failed to add organization"}), 500

    if auth.check_role(username) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if org.check_organization_name_exist(name):
        db.close()
        return jsonify({"message": "Organization name exists"}), 500

    success = org.add_organization(name, contact_phone, contact_email, description, username, org_member)

    db.close()

    if success:
        return jsonify({"message": "Organization added successfully"}), 200
    else:
        return jsonify({"message": "Failed to add organization"}), 500

@organization_bp.route("/get", methods=["GET"])
def get_organization():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    if session.get("username") == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    username = session["username"]
    organization_data = org.get_all_organizations(username)

    db.close()

    if organization_data:
        return jsonify(organization_data), 200
    else:
        return jsonify({"message": "Organization not found"}), 404

@organization_bp.route("/get/<organization_id>", methods=["GET"])
def get_organization_by_id(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    if session.get("username") == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    username = session["username"]

    if org.check_user_access(username, organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
   
    organization_data = org.get_organization_by_id(username, organization_id)

    db.close()

    if organization_data:
        return jsonify(organization_data), 200
    else:
        return jsonify({"message": "Organization not found"}), 404
    
@organization_bp.route("/change_organization_status", methods=["PUT"])
def change_organization_status():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    if session.get("username") == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_id = request.json["organization_id"]
    status = request.json["status"]

    if org.check_user_access(session["username"], organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = org.change_organization_status(organization_id, status)

    db.close()

    if success:
        return jsonify({"message": "Organization status changed successfully"}), 200
    else:
        return jsonify({"message": "Failed to change organization status"}), 500
    

@organization_bp.route("/update_information", methods=["PUT"])
def update_organization_information():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    if session.get("username") == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_id = request.json["organization_id"]
    name = request.json["name"]
    contact_phone = request.json["contact_phone"]
    contact_email = request.json["contact_email"]
    description = request.json["description"]

    if org.check_user_access(session["username"], organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = org.update_information(name, contact_phone, contact_email, description, organization_id)

    db.close()

    if success:
        return jsonify({"message": "Organization information updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update organization information"}), 500

@organization_bp.route("/add_user", methods=["PUT"])
def add_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    if session.get("username") == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_id = request.json["organization_id"]
    new_user = request.json["new_user"]

    if org.check_user_access(session["username"], organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = org.add_user(organization_id, new_user)

    db.close()

    if success:
        return jsonify({"message": "User added to organization successfully"}), 200
    else:
        return jsonify({"message": "Error adding user to organization:"}), 500

@organization_bp.route("/remove_user", methods=["PUT"])
def remove_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    if session.get("username") == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_id = request.json["organization_id"]
    remove_username = request.json["remove_username"]

    if org.check_user_access(session["username"], organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = org.remove_user(organization_id, remove_username)

    db.close()

    if success:
        return jsonify({"message": "User removed from organization successfully"}), 200
    else:
        return jsonify({"message": "Failed to remove user from organization"}), 500

@organization_bp.route("/get_number_of_users/<organization_id>", methods=["GET"])
def get_number_of_users(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    if session.get("username") == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if org.check_user_access(session["username"], organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    try:
        number_users = org.get_number_of_users(organization_id)
        db.close()
        return jsonify({"number_users": number_users}), 200
    except Exception as e:
        db.close()
        print("Error getting number of users:", e)
        return jsonify({"message": "Failed to get number of users"}), 500


@organization_bp.route("/get_organization_data/<organization_id>", methods=["GET"])
def get_organization_data_by_id(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)
    auth = Auth(db)

    if session.get("username") == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if org.check_user_access(session["username"], organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if auth.check_role(session["username"]) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    try:
        organization_data = org.get_organization_data(organization_id)
        db.close()
        if organization_data:
            return jsonify(organization_data), 200
        else:
            return jsonify({"message": "Organization not found"}), 404
    except Exception as e:
        db.close()
        print("Error getting organization data:", e)
        return jsonify({"message": "Failed to get organization data"}), 500
