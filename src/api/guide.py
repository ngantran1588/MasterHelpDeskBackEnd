from flask import jsonify, request, Blueprint
from ..database.load_env import LoadDBEnv
from ..database.guide import Guide
from ..database import connector
from ..decorators import token_required

guide_bp = Blueprint("guide", __name__)

@guide_bp.route("/get", methods=["GET"])
def get_guides():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    db.connect()
    guide = Guide(db)
    
    guide_data = guide.get_guides()

    db.close()

    if guide_data:
        return jsonify(guide_data), 200
    else:
        return jsonify({"message": "Guide not found"}), 404

@guide_bp.route("/get/<guide_id>", methods=["GET"])
def get_guide(guide_id):
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        guide = Guide(db)

        if not guide_id:
            return jsonify({"message": "Guide ID is required."}), 400
        
        guide_data = guide.get_guide_by_id(guide_id)

        db.close()

        if guide_data:
            return jsonify(guide_data), 200
        else:
            return jsonify({"message": "Guide not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@guide_bp.route("/add", methods=["POST"])
@token_required
def add_guide():
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        guide = Guide(db)

        username = request.jwt_payload.get("manager_username")

        if username == None:
            db.close()
            return jsonify({"message": "Permission denied"}), 403
        
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")

        if not title and not content:
            return jsonify({"error": "Title or content is required"}), 400

        success = guide.add_guide(title, content)

        db.close()

        if success:
            return jsonify({"message": "Guide added successfully"}), 201
        else:
            return jsonify({"message": "Failed to add guide"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@guide_bp.route("/update/<guide_id>", methods=["PUT"])
@token_required
def update_guide(guide_id):
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        guide = Guide(db)

        username = request.jwt_payload.get("manager_username")

        if username == None:
            db.close()
            return jsonify({"message": "Permission denied"}), 403
        
        if not guide_id:
            return jsonify({"message": "Guide ID is required."}), 400
        
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")

        if not title and not content:
            return jsonify({"error": "Title or content is required"}), 400

        success = guide.update_guide(guide_id, title, content)

        db.close()

        if success:
            return jsonify({"message": "Guide updated successfully"}), 200
        else:
            return jsonify({"message": "Failed to update guide"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@guide_bp.route("/delete/<guide_id>", methods=["DELETE"])
@token_required
def delete_guide(guide_id):
    try:
        db_env = LoadDBEnv.load_db_env()
        db = connector.DBConnector(*db_env)
        db.connect()
        guide = Guide(db)

        username = request.jwt_payload.get("manager_username")

        if username == None:
            db.close()
            return jsonify({"message": "Permission denied"}), 403

        if not guide_id:
            return jsonify({"message": "Guide ID is required."}), 400
        
        success = guide.delete_guide(guide_id)

        db.close()

        if success:
            return jsonify({"message": "Guide deleted successfully"}), 200
        else:
            return jsonify({"message": "Failed to delete guide"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
