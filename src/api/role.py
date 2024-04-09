from flask import jsonify, request, Blueprint
from ..database.load_env import LoadDBEnv
from ..database.role import Role
from ..database import connector

role_bp = Blueprint("role", __name__)

@role_bp.route("/get", methods=["GET"])
def get_roles():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    role = Role(db)
    
    role_data = role.get_roles()

    db.close()

    if role_data:
        return jsonify(role_data), 200
    else:
        return jsonify({"message": "Organization not found"}), 404

@role_bp.route("/get/<role_id>", methods=["GET"])
def get_role(role_id):
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        role = Role(db)
        
        role_data = role.get_role_by_id(role_id)

        db.close()

        if role_data:
            return jsonify(role_data), 200
        else:
            return jsonify({"message": "role not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@role_bp.route("/add", methods=["POST"])
def add_role():
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        role = Role(db)
        
        data = request.get_json()
        role_name = data.get("role_name")
        description = data.get("description")

        if not role_name and not description:
            return jsonify({"error": "role_name or description is required"}), 400

        success = role.add_role(role_name, description)

        db.close()

        if success:
            return jsonify({"message": "role added successfully"}), 201
        else:
            return jsonify({"message": "Failed to add role"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@role_bp.route("/update/<role_id>", methods=["PUT"])
def update_role(role_id):
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        role = Role(db)
        
        data = request.get_json()
        role_name = data.get("role_name")
        description = data.get("description")

        if not role_name and not description:
            return jsonify({"error": "role_name or description is required"}), 400

        success = role.update_role(role_id, role_name, description)

        db.close()

        if success:
            return jsonify({"message": "role updated successfully"}), 200
        else:
            return jsonify({"message": "Failed to update role"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@role_bp.route("/delete/<role_id>", methods=["DELETE"])
def delete_role(role_id):
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        role = Role(db)
        
        success = role.delete_role(role_id)

        db.close()

        if success:
            return jsonify({"message": "role deleted successfully"}), 200
        else:
            return jsonify({"message": "Failed to delete role"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
