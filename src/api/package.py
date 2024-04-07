from flask import Blueprint, jsonify
from ..database import connector
from ..database.package import Package
from ..database.load_env import LoadDBEnv

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
    
    data = package.get_package_by_id(package_id)

    if len(data) != 0:
        db.close()
        return jsonify(data), 200
    else:
        db.close()
        return jsonify({"message": "No data returned"}), 500