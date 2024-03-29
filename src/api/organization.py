from flask import Blueprint, request, jsonify, session
from ..database import connector
from ..database.organization import Organization 
from ..database.load_env import LoadDBEnv
from ..database.auth import Auth

organization_bp = Blueprint("organization", __name__)

@organization_bp.route("/add", methods=["POST"])
def add_organization():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)
    auth = Auth(db)
    
    data = request.get_json()
    name = data["name"]
    contact_phone = data["contact_phone"]
    contact_email = data["contact_email"]
    description = data["description"]
    username = session["username"]
    org_member = data["org_member"]

    if org.check_organization_slot(username) == False:
        return jsonify({"message": "Failed to add organization"}), 500

    if auth.check_role(username) == False:
        return jsonify({"message": "Permission denied"}), 403

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

    username = session["username"]
    organization_data = org.get_all_organizations(username)

    db.close()

    if organization_data:
        return jsonify(organization_data), 200
    else:
        return jsonify({"message": "Organization not found"}), 404

@organization_bp.route("/get/<organization_id>", methods=["GET"])
def get_organization(organization_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    org = Organization(db)

    username = session["username"]

    if org.check_user_access(username, organization_id) == False:
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

    organization_id = request.json["organization_id"]
    status = request.json["status"]

    if org.check_user_access(session["username"], organization_id) == False:
        return jsonify({"message": "Permission denied"}), 403
    
    success = org.change_organization_status(organization_id, status)

    db.close()

    if success:
        return jsonify({"message": "Organization status changed successfully"}), 200
    else:
        return jsonify({"message": "Failed to change organization status"}), 500