from flask import Blueprint, jsonify, request
from ..database import connector
from ..database.package import Package
from ..database.load_env import LoadDBEnv
from ..decorators import token_required

package_bp = Blueprint("package", __name__)

@package_bp.route("/get", methods=["GET"])
def get_all_package():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    package = Package(db)
    
    data = package.get_packages()

    if len(data) != 0:
        db.close()
        return jsonify(data), 200
    else:
        db.close()
        return jsonify({"message": "No data returned"}), 500
    
@package_bp.route("/get/<package_id>", methods=["GET"])
def get_package_by_id(package_id):
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    package = Package(db)

    if not package_id:
        return jsonify({"message": "Package ID is required."}), 400
    
    data = package.get_package_by_id(package_id)

    if len(data) != 0:
        db.close()
        return jsonify(data), 200
    else:
        db.close()
        return jsonify({"message": "No data returned"}), 500
    
@package_bp.route("/add", methods=["POST"])
@token_required
def add_package():
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        package = Package(db)
        
        username = request.jwt_payload.get("manager_username")

        if username == None:
            db.close()
            return jsonify({"message": "Permission denied"}), 403
        
        data = request.get_json()
        package_name = data.get("package_name")
        duration = data.get("duration")
        description = data.get("description")
        slot_number = data.get("slot_number")
        slot_server = data.get("slot_server")
        price = data.get("price")
        status = data.get("status")

        if not package_name and not duration and not description and not slot_number and not slot_server and not price and not status:
            return jsonify({"error": "Fields are missing"}), 400

        success = package.add_package(package_name, duration, description, slot_number, slot_server, price, status)

        db.close()

        if success:
            return jsonify({"message": "package added successfully"}), 201
        else:
            return jsonify({"message": "Failed to add package"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@package_bp.route("/update/<package_id>", methods=["PUT"])
@token_required
def update_package(package_id):
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        package = Package(db)

        username = request.jwt_payload.get("manager_username")

        if username == None:
            db.close()
            return jsonify({"message": "Permission denied"}), 403

        if not package_id:
            return jsonify({"message": "Package ID is required."}), 400
        
        data = request.get_json()
        package_id = data.get("package_id")
        package_name = data.get("package_name")
        duration = data.get("duration")
        description = data.get("description")
        slot_number = data.get("slot_number")
        slot_server = data.get("slot_server")
        price = data.get("price")
        status = data.get("status")

        if not package_id and not package_name and not duration and not description and not slot_number and not slot_server and not price and not status:
            return jsonify({"error": "Fields are missing"}), 400

        success = package.update_package(package_id, package_name, duration, description, slot_number, slot_server, price, status)

        db.close()

        if success:
            return jsonify({"message": "package updated successfully"}), 200
        else:
            return jsonify({"message": "Failed to update package"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@package_bp.route("/delete/<package_id>", methods=["DELETE"])
@token_required
def delete_package(package_id):
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        package = Package(db)

        username = request.jwt_payload.get("manager_username")

        if username == None:
            db.close()
            return jsonify({"message": "Permission denied"}), 403
        
        if not package_id:
            return jsonify({"message": "Package ID is required."}), 400
        
        success = package.delete_package(package_id)

        db.close()

        if success:
            return jsonify({"message": "package deleted successfully"}), 200
        else:
            return jsonify({"message": "Failed to delete package"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
