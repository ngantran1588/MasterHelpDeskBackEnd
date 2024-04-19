from flask import jsonify, request, Blueprint
from ..database.load_env import LoadDBEnv
from ..database.subscription import Subscription
from ..database import connector
from ..decorators import token_required

subscription_bp = Blueprint("subscription", __name__)
@subscription_bp.route("/check_subscription_by_username", methods=["GET"])
@token_required
def check_subscription_by_username():
    db_env = LoadDBEnv.load_db_env()
    db = connector.DBConnector(*db_env)
    sub = Subscription(db)
    
    username = request.jwt_payload.get("username")
    if username == None:
        db.close()
        return jsonify({"message": "Permission denied"}), 403
    sub_data = sub.check_subscription_by_username(username)
    db.close()

    if sub_data:
        return jsonify({"message": "Subcription bought !"}), 200
    else:
        return jsonify({"message": "Subcription not found"}), 500
