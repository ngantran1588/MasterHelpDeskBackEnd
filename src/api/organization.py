from flask import Blueprint, request, jsonify
from ..database import connector
from ..database.organization import Organization 
from ..database.load_env import LoadDBEnv
from ..database.auth import Auth
from ..decorators import token_required

organization_bp = Blueprint("organization", __name__)

@organization_bp.route("/add", methods=["POST"])
@token_required
def add_organization():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)
    auth = Auth(db)

    username = request.jwt_payload.get("username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    data = request.get_json()
    name = data["name"]
    contact_phone = data["contact_phone"]
    contact_email = data["contact_email"]
    description = data["description"]
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

    for member in org_member:
        if not auth.exist_username(member):
            db.close()
            return jsonify({"message": "User does not exist"}), 500

    success = org.add_organization(name, contact_phone, contact_email, description, username, org_member)

    db.close()

    if success:
        return jsonify({"message": "Organization added successfully"}), 200
    else:
        return jsonify({"message": "Failed to add organization"}), 500

@organization_bp.route("/get", methods=["GET"])
@token_required
def get_organization():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    username = request.jwt_payload.get("username")
   
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_data = org.get_all_organizations(username)

    db.close()

    if organization_data:
        return jsonify(organization_data), 200
    else:
        return jsonify({"message": "Organization not found"}), 404

@organization_bp.route("/get/<organization_id>", methods=["GET"])
@token_required
def get_organization_by_id(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

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
@token_required
def change_organization_status():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_id = request.json["organization_id"]
    status = request.json["status"]

    if org.check_user_access(username, organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = org.change_organization_status(organization_id, status)

    db.close()

    if success:
        return jsonify({"message": "Organization status changed successfully"}), 200
    else:
        return jsonify({"message": "Failed to change organization status"}), 500
    

@organization_bp.route("/update_information", methods=["PUT"])
@token_required
def update_organization_information():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_id = request.json["organization_id"]
    name = request.json["name"]
    contact_phone = request.json["contact_phone"]
    contact_email = request.json["contact_email"]
    description = request.json["description"]

    if org.check_user_access(username, organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = org.update_information(name, contact_phone, contact_email, description, organization_id)

    db.close()

    if success:
        return jsonify({"message": "Organization information updated successfully"}), 200
    else:
        return jsonify({"message": "Failed to update organization information"}), 500

@organization_bp.route("/add_user", methods=["PUT"])
@token_required
def add_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_id = request.json["organization_id"]
    new_user = request.json["new_user"]

    if org.check_user_access(username, organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = org.add_user(organization_id, new_user)

    db.close()

    if success:
        return jsonify({"message": "User added to organization successfully"}), 200
    else:
        return jsonify({"message": "Error adding user to organization:"}), 500

@organization_bp.route("/remove_user", methods=["PUT"])
@token_required
def remove_user():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_id = request.json["organization_id"]
    remove_username = request.json["remove_username"]

    if org.check_user_access(username, organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    success = org.remove_user(organization_id, remove_username)

    db.close()

    if success:
        return jsonify({"message": "User removed from organization successfully"}), 200
    else:
        return jsonify({"message": "Failed to remove user from organization"}), 500

@organization_bp.route("/get_number_of_users/<organization_id>", methods=["GET"])
@token_required
def get_number_of_users(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if org.check_user_access(username, organization_id) == False:
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
@token_required
def get_organization_data_by_id(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)
    auth = Auth(db)

    username = request.jwt_payload.get("username")

    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    if org.check_user_access(username, organization_id) == False:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    
    if auth.check_role(username) == False:
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

@organization_bp.route("/delete", methods=["DELETE"])
@token_required
def delete_organization():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    username = request.jwt_payload.get("username")

    if username is None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    organization_id = request.json.get("organization_id")

    if organization_id is None:
        db.close()
        return jsonify({"message": "Organization ID is missing"}), 400

    # Check if the user has access to delete the organization
    if not org.check_user_access(username, organization_id):
        db.close()
        return jsonify({"message": "Permission denied"}), 403

    # Attempt to delete the organization
    success = org.delete_organization(organization_id)

    db.close()

    if success:
        return jsonify({"message": "Organization deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete organization"}), 500
